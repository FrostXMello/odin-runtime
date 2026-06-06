from __future__ import annotations
from typing import Any


class RegressionForecastRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app

    async def forecast(self, *, change: str) -> dict[str, Any]:
        risk = min(1.0, len(change) / 500.0)
        payload = {"change": change[:120], "risk": risk, "approval_required": True}
        self._emit("engineering_regression_forecasted", payload)
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
        obs.tracer.record(kind, message=kind_name, payload=payload, component="regression_forecast")
