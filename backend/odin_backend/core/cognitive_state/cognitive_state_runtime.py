"""Cognitive state runtime (Prompt 52)."""
from __future__ import annotations
from typing import Any


class CognitiveStateRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._mode = "balanced"

    async def compute_cognitive_state(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "cognitive_state_enabled", False):
            return {"accepted": False, "reason": "cognitive_state_disabled"}
        pressure = await self.estimate_runtime_pressure()
        engagement = await self.estimate_operator_load()
        state = {
            "mode": self._mode,
            "cognitive_pressure": pressure.get("pressure", 0.4),
            "operator_engagement": engagement.get("load", 0.5),
            "focus_depth": 0.6,
            "memory_saturation": 0.3,
        }
        self._emit("cognitive_state_updated", state)
        return {"accepted": True, "state": state}

    async def estimate_operator_load(self) -> dict[str, Any]:
        load = 0.5
        if hasattr(self._app, "operator_intelligence_v4"):
            r = await self._app.operator_intelligence_v4.predict(hours=4.0)
            if r.get("accepted"):
                load = r.get("load_forecast", {}).get("forecast_load", 0.5)
        return {"accepted": True, "load": load}

    async def estimate_runtime_pressure(self) -> dict[str, Any]:
        pressure = 0.4
        if hasattr(self._app, "cognitive_scheduler"):
            snap = self._app.cognitive_scheduler.snapshot()
            pressure = min(1.0, (snap.get("active", 0) + snap.get("deferred", 0)) / 32.0)
        return {"accepted": True, "pressure": pressure}

    async def export_state_snapshot(self) -> dict[str, Any]:
        return await self.compute_cognitive_state()

    def snapshot(self) -> dict[str, Any]:
        return {"mode": self._mode}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="cognitive_state")
