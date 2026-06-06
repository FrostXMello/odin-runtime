from __future__ import annotations
from typing import Any


class DeepFocusCoordinator:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._active = False

    async def start(self, *, minutes: int = 45) -> dict[str, Any]:
        if not getattr(self._app.settings, "deep_focus_enabled", False):
            return {"accepted": False, "reason": "deep_focus_disabled"}
        self._active = True
        payload = {"minutes": min(minutes, 120), "interruptions_minimized": True}
        self._emit("deep_focus_session_started", payload)
        return {"accepted": True, **payload, "operator_controlled": True}

    def snapshot(self) -> dict[str, Any]:
        return {"active": self._active}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="deep_focus")
