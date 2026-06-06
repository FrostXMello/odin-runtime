"""Model orchestration runtime."""

from __future__ import annotations

from typing import Any

from odin_backend.core.local_ai.model_orchestration import (
    bind_memory,
    lightweight_plan,
    route_reasoning,
    schedule_deep_reasoning,
    specialize_inference,
)


class ModelOrchestrationRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._routes = 0

    async def route(self, *, task: str, complexity: float = 0.5) -> dict[str, Any]:
        if not getattr(self._app.settings, "model_orchestration_enabled", False):
            return {"accepted": False, "reason": "model_orchestration_disabled"}
        vram = getattr(self._app.settings, "local_ai_vram_mb", 4096)
        on_battery = getattr(self._app.settings, "on_battery", False)
        routed = route_reasoning(complexity=complexity, vram_mb=vram, on_battery=on_battery)
        specialized = specialize_inference(task=task)
        schedule = schedule_deep_reasoning(queue_depth=0, vram_free_mb=vram)
        memory_ids: list[str] = []
        if hasattr(self._app, "vector_memory"):
            memory_ids = [str(i) for i in range(min(3, self._app.vector_memory.snapshot().get("long_term", 0)))]
        binding = bind_memory(model=routed["model"], memory_ids=memory_ids)
        self._routes += 1
        self._emit("model_route_selected", {"model": routed["model"], "task": task[:60], "specialized": specialized})
        return {"accepted": True, "route": routed, "specialized": specialized, "schedule": schedule, "binding": binding}

    async def plan(self, *, goal: str) -> dict[str, Any]:
        return {"accepted": True, **lightweight_plan(goal=goal)}

    def snapshot(self) -> dict[str, Any]:
        return {"routes": self._routes}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="model_orchestration")
