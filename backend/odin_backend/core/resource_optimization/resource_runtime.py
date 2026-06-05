"""Consumer hardware resource optimization."""

from __future__ import annotations

from typing import Any

from odin_backend.core.resource_optimization.adaptive_loading import should_load
from odin_backend.core.resource_optimization.battery_aware_runtime import throttle_factor
from odin_backend.core.resource_optimization.idle_compaction import compact
from odin_backend.core.resource_optimization.lightweight_modes import mode_config
from odin_backend.core.resource_optimization.memory_pressure_runtime import pressure_level
from odin_backend.core.resource_optimization.model_swapper import ModelSwapper


class ResourceOptimizationRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._swapper = ModelSwapper()
        self._mode = getattr(app.settings, "resource_mode", "normal")

    async def optimize(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "resource_optimization_enabled", False):
            return {"accepted": False, "reason": "resource_optimization_disabled"}
        ram_mb = getattr(self._app.settings, "local_ai_ram_mb", 16384)
        used_mb = ram_mb // 2
        pressure = pressure_level(used_mb=used_mb, total_mb=ram_mb)
        evicted = []
        if pressure["level"] in ("high", "critical"):
            evicted = await self._swapper.evict_under_pressure(self._app)
        config = mode_config(self._mode)
        battery = throttle_factor(on_battery=getattr(self._app.settings, "on_battery", False), battery_pct=80)
        cache_compact = compact(cache_size=50)
        self._emit("resource_optimized", {"pressure": pressure["level"], "evicted": len(evicted)})
        return {"accepted": True, "pressure": pressure, "evicted": evicted, "mode_config": config, "battery_throttle": battery, "compaction": cache_compact}

    def set_mode(self, mode: str) -> dict[str, Any]:
        self._mode = mode
        return mode_config(mode)

    def snapshot(self) -> dict[str, Any]:
        vram = getattr(self._app.settings, "local_ai_vram_mb", 4096)
        ram = getattr(self._app.settings, "local_ai_ram_mb", 16384)
        return {"mode": self._mode, "vram_mb": vram, "ram_mb": ram, "mode_config": mode_config(self._mode)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="resource_optimization")
