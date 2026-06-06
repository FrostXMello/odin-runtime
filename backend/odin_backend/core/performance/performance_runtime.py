"""Performance orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.performance.adaptive_batching import batch_size
from odin_backend.core.performance.cpu_fallbacks import use_cpu_fallback
from odin_backend.core.performance.gpu_allocator import allocate_vram
from odin_backend.core.performance.inference_scheduler import schedule_inference
from odin_backend.core.performance.io_scheduler import io_priority
from odin_backend.core.performance.lazy_loading import should_lazy_load
from odin_backend.core.performance.memory_pressure_manager import pressure_action
from odin_backend.core.performance.startup_optimizer import optimize_startup
from odin_backend.core.resource_optimization.memory_pressure_runtime import pressure_level


class PerformanceRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._optimizations = 0

    async def optimize(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "performance_enabled", False):
            return {"accepted": False, "reason": "performance_disabled"}
        ram = getattr(self._app.settings, "local_ai_ram_mb", 16384)
        vram = getattr(self._app.settings, "local_ai_vram_mb", 4096)
        pressure = pressure_level(used_mb=ram // 2, total_mb=ram)
        actions = pressure_action(pressure["level"])
        schedule = schedule_inference(queue_depth=0, vram_pressure=pressure["level"])
        batch = batch_size(mode=getattr(self._app.settings, "survival_mode", "balanced"), ram_mb=ram)
        cpu_fb = use_cpu_fallback(vram_pressure=pressure["level"], on_battery=getattr(self._app.settings, "on_battery", False))
        gpu = allocate_vram(requested_mb=2048, available_mb=vram)
        if actions.get("evict_models") and hasattr(self._app, "local_ai"):
            for m in list(getattr(self._app.local_ai, "_loaded", set())):
                await self._app.local_ai.evict(m)
                self._emit("model_swapped", {"evicted": m})
        if pressure["level"] in ("high", "critical"):
            self._emit("memory_pressure_detected", pressure)
        self._optimizations += 1
        self._emit("startup_optimized", {"batch": batch, "cpu_fallback": cpu_fb})
        return {
            "accepted": True,
            "pressure": pressure,
            "actions": actions,
            "schedule": schedule,
            "batch_size": batch,
            "cpu_fallback": cpu_fb,
            "gpu": gpu,
            "io_priority": io_priority(background=getattr(self._app.settings, "daemon_mode_enabled", False)),
        }

    async def optimize_startup(self) -> dict[str, Any]:
        plan = optimize_startup(components=["local_ai", "vector_memory", "daemon", "project_os"])
        return {"accepted": True, **plan}

    def snapshot(self) -> dict[str, Any]:
        return {"optimizations": self._optimizations, "lazy_local_ai": should_lazy_load(component="local_ai", idle=True)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="performance")
