from __future__ import annotations
from typing import Any


class ReliabilityPredictionRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app

    async def predict(self, *, change: str) -> dict[str, Any]:
        if not getattr(self._app.settings, "reliability_forecasting_enabled", False):
            return {"accepted": False, "reason": "reliability_forecasting_disabled"}
        risk = min(1.0, len(change) / 400.0)
        payload = {"change": change[:120], "risk": risk, "approval_required": True}
        if risk > 0.5:
            self._emit("reliability_risk_detected", payload)
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
        obs.tracer.record(kind, message=kind_name, payload=payload, component="reliability_prediction")
