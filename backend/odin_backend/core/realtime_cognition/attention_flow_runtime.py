"""Attention flow runtime (Prompt 51)."""
from __future__ import annotations
from typing import Any


class AttentionFlowRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._focus = "workspace"

    async def route(self, *, focus: str) -> dict[str, Any]:
        if not getattr(self._app.settings, "realtime_cognition_enabled", False):
            return {"accepted": False, "reason": "realtime_cognition_disabled"}
        self._focus = focus[:60]
        self._emit("attention_flow_updated", {"focus": self._focus})
        return {"accepted": True, "focus": self._focus, "bounded": True}

    def snapshot(self) -> dict[str, Any]:
        return {"focus": self._focus}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="attention_flow")
