"""Operator focus runtime (Prompt 54)."""
from __future__ import annotations
from typing import Any


class OperatorFocusRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._active = False
        self._minutes = 0

    async def start_focus_session(self, *, minutes: int = 45) -> dict[str, Any]:
        if not getattr(self._app.settings, "operator_focus_enabled", False):
            return {"accepted": False, "reason": "operator_focus_disabled"}
        self._active = True
        self._minutes = min(minutes, 120)
        self._emit("focus_session_started", {"minutes": self._minutes})
        if hasattr(self._app, "operator_intelligence_v3"):
            await self._app.operator_intelligence_v3.start_deep_focus(minutes=self._minutes)
        return {"accepted": True, "active": True, "minutes": self._minutes, "operator_controlled": True}

    async def estimate_distraction_pressure(self) -> dict[str, Any]:
        pressure = 0.3
        if hasattr(self._app, "window_awareness"):
            snap = self._app.window_awareness.snapshot()
            if snap.get("active", {}).get("app") in ("slack", "discord"):
                pressure = 0.8
        return {"accepted": True, "pressure": pressure, "transparent": True}

    async def detect_focus_breakdown(self) -> dict[str, Any]:
        broken = self._active and self._minutes > 90
        if broken:
            self._emit("focus_breakdown_detected", {"minutes": self._minutes})
        return {"accepted": True, "breakdown": broken}

    async def recommend_focus_recovery(self) -> dict[str, Any]:
        return {"accepted": True, "recommendation": "short_break", "operator_override": True}

    def snapshot(self) -> dict[str, Any]:
        return {"active": self._active, "minutes": self._minutes}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="operator_focus")
