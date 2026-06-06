from __future__ import annotations
from typing import Any


class CognitiveLoadForecastRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app

    async def forecast(self, *, hours: float) -> dict[str, Any]:
        load = min(1.0, hours / 8.0)
        payload = {"hours": hours, "forecast_load": load}
        self._emit("cognitive_load_forecasted", payload)
        return {"accepted": True, **payload, "local_only": True}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="cognitive_load_forecast")
