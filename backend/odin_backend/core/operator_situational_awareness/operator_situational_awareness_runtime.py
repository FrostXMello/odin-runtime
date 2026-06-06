"""Operator situational awareness runtime (Prompt 56)."""
from __future__ import annotations
from typing import Any


class OperatorSituationalAwarenessRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._pressure = 0.4

    async def generate_operator_brief(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "operator_situational_awareness_enabled", False):
            return {"accepted": False, "reason": "operator_situational_awareness_disabled"}
        brief = {"summary": "runtime operational", "supervised": True, "local_only": True}
        self._emit("operator_brief_generated", {"brief": "generated"})
        return {"accepted": True, "brief": brief, "transparent": True}

    async def estimate_operational_pressure(self) -> dict[str, Any]:
        if hasattr(self._app, "operator_focus"):
            p = await self._app.operator_focus.estimate_distraction_pressure()
            self._pressure = p.get("pressure", 0.4)
        self._emit("operational_pressure_forecasted", {"pressure": self._pressure})
        return {"accepted": True, "pressure": round(self._pressure, 2), "operator_visible": True}

    async def forecast_focus_instability(self) -> dict[str, Any]:
        risk = self._pressure > 0.7
        return {"accepted": True, "risk": risk, "bounded": True}

    async def summarize_runtime_state(self) -> dict[str, Any]:
        state = {}
        if hasattr(self._app, "live_orchestration"):
            state["orchestration"] = self._app.live_orchestration.snapshot()
        return {"accepted": True, "state": state, "local_first": True}

    def snapshot(self) -> dict[str, Any]:
        return {"pressure": self._pressure}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="operator_situational_awareness")
