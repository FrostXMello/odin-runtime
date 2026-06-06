from __future__ import annotations
from typing import Any


class ArchitectureForecastEngine:
    def __init__(self, app: Any) -> None:
        self._app = app

    async def forecast(self, *, horizon_days: int = 30) -> dict[str, Any]:
        payload = {"horizon_days": min(horizon_days, 90), "forecast": "stable", "supervised": True}
        self._emit("architecture_forecast_generated", payload)
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
        obs.tracer.record(kind, message=kind_name, payload=payload, component="architecture_forecast")
