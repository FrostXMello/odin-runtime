from __future__ import annotations
from typing import Any


class BurnoutAwarenessRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app

    async def assess(self, *, hours: float) -> dict[str, Any]:
        risk = hours > 6.0
        payload = {"hours": hours, "burnout_risk": risk, "transparent": True}
        if risk:
            self._emit("burnout_risk_detected", payload)
        return {"accepted": True, **payload, "operator_override": True}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="burnout_awareness")
