"""Task orchestration runtime (Prompt 57)."""
from __future__ import annotations
from typing import Any


class TaskOrchestrationRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._queue: list[dict] = []
        self._mode = "adaptive"

    async def build_execution_pipeline(self, *, stages: list[str] | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "task_orchestration_enabled", False):
            return {"accepted": False, "reason": "task_orchestration_disabled"}
        pipeline = (stages or ["plan", "review", "execute"])[:12]
        self._queue = [{"stage": s, "priority": i} for i, s in enumerate(pipeline)]
        return {"accepted": True, "pipeline": pipeline, "supervised": True}

    async def reprioritize_execution_queue(self) -> dict[str, Any]:
        self._queue.sort(key=lambda x: x.get("priority", 0))
        self._emit("execution_queue_rebalanced", {"size": len(self._queue)})
        return {"accepted": True, "queue_size": len(self._queue), "bounded": len(self._queue) <= 64}

    async def detect_execution_blockers(self) -> dict[str, Any]:
        blockers = [q for q in self._queue if q.get("blocked")]
        if blockers:
            self._emit("execution_blocker_detected", {"count": len(blockers)})
        return {"accepted": True, "blockers": blockers, "operator_visible": True}

    async def recover_interrupted_pipeline(self) -> dict[str, Any]:
        if hasattr(self._app, "execution_system"):
            return await self._app.execution_system.rollback_execution_stage()
        return {"accepted": True, "recovered": False}

    def snapshot(self) -> dict[str, Any]:
        return {"queue_size": len(self._queue), "mode": self._mode}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="task_orchestration")
