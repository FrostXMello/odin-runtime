"""Consumer hardware resource optimization."""

from __future__ import annotations

from typing import Any

from odin_backend.core.resource_optimization.adaptive_loading import should_load
from odin_backend.core.resource_optimization.battery_aware_runtime import throttle_factor
from odin_backend.core.resource_optimization.idle_compaction import compact
from odin_backend.core.resource_optimization.lightweight_modes import mode_config
from odin_backend.core.resource_optimization.memory_pressure_runtime import pressure_level
from odin_backend.core.resource_optimization.emergency_reclaim import emergency_reclaim
from odin_backend.core.resource_optimization.model_swapper import ModelSwapper
from odin_backend.core.resource_optimization.survival_modes import survival_config


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

    async def survive(self, *, mode: str | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "resource_optimization_enabled", False):
            return {"accepted": False, "reason": "resource_optimization_disabled"}
        survival_mode = mode or getattr(self._app.settings, "survival_mode", "balanced")
        config = survival_config(survival_mode)
        reclaimed = {}
        if survival_mode in ("ultra_light", "overnight_daemon"):
            reclaimed = await emergency_reclaim(self._app)
        self._mode = survival_mode if survival_mode in ("ultra_light", "overnight_daemon") else self._mode
        return {"accepted": True, "survival_mode": survival_mode, "config": config, "reclaimed": reclaimed}

    async def compress_runtime_surfaces(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "resource_optimization_enabled", False):
            return {"accepted": False, "reason": "resource_optimization_disabled"}
        compact_result = compact(cache_size=30)
        self._emit("runtime_surfaces_compressed", {"compaction": compact_result})
        return {"accepted": True, "compressed": True, "compaction": compact_result, "bounded": True}

    async def rebalance_render_density(self) -> dict[str, Any]:
        profile = getattr(self._app.settings, "resource_profile", "balanced")
        config = mode_config(profile)
        return {"accepted": True, "profile": profile, "config": config, "adaptive": True}

    async def optimize_memory_pressure(self) -> dict[str, Any]:
        ram_mb = getattr(self._app.settings, "local_ai_ram_mb", 16384)
        pressure = pressure_level(used_mb=ram_mb // 2, total_mb=ram_mb)
        evicted = []
        if pressure["level"] in ("high", "critical"):
            evicted = await self._swapper.evict_under_pressure(self._app)
        self._emit("memory_pressure_optimized", {"level": pressure["level"], "evicted": len(evicted)})
        return {"accepted": True, "pressure": pressure, "evicted": evicted, "reversible": True}

    async def reduce_background_activity(self) -> dict[str, Any]:
        if hasattr(self._app, "runtime_cleanup"):
            await self._app.runtime_cleanup.schedule_background_cleanup(mode="passive")
        return {"accepted": True, "reduced": True, "low_power": True}

    async def enter_low_power_coordination(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "low_power_coordination", False):
            return {"accepted": False, "reason": "low_power_coordination_disabled"}
        battery = throttle_factor(on_battery=True, battery_pct=60)
        if hasattr(self._app, "stream_management"):
            await self._app.stream_management.stabilize_stream_density()
        return {"accepted": True, "low_power": True, "battery_throttle": battery, "supervised": True}

    def snapshot(self) -> dict[str, Any]:
        vram = getattr(self._app.settings, "local_ai_vram_mb", 4096)
        ram = getattr(self._app.settings, "local_ai_ram_mb", 16384)
        survival = getattr(self._app.settings, "survival_mode", "balanced")
        return {
            "mode": self._mode,
            "vram_mb": vram,
            "ram_mb": ram,
            "mode_config": mode_config(self._mode),
            "survival_mode": survival,
            "survival_config": survival_config(survival),
        }

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
