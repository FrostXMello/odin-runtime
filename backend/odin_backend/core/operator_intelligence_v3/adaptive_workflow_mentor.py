from __future__ import annotations
from typing import Any


class AdaptiveWorkflowMentor:
    def __init__(self, app: Any) -> None:
        self._app = app

    async def recommend(self, *, context: str) -> dict[str, Any]:
        workflow = {"context": context[:80], "steps": ["focus", "review", "break"], "transparent": True}
        self._emit("adaptive_workflow_generated", workflow)
        return {"accepted": True, "workflow": workflow}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="workflow_mentor")
