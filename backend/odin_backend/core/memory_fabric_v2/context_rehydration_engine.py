from __future__ import annotations
from typing import Any


class ContextRehydrationEngine:
    def __init__(self, app: Any) -> None:
        self._app = app

    async def rehydrate(self, *, session: str) -> dict[str, Any]:
        if not getattr(self._app.settings, "context_rehydration_enabled", False):
            return {"accepted": False, "reason": "context_rehydration_disabled"}
        payload = {"session": session[:80], "restored": True}
        self._emit("context_rehydrated", payload)
        if hasattr(self._app, "memory_fabric"):
            await self._app.memory_fabric.recall(query=session)
        return {"accepted": True, **payload}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="context_rehydration")
