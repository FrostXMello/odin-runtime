"""Intervention intelligence runtime (Prompt 58)."""
from __future__ import annotations
from typing import Any


class InterventionIntelligenceRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._overload = 0.3
        self._escalation = 0.2

    async def forecast_operator_intervention(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "intervention_intelligence_enabled", False):
            return {"accepted": False, "reason": "intervention_intelligence_disabled"}
        if hasattr(self._app, "operator_situational_awareness"):
            p = await self._app.operator_situational_awareness.estimate_operational_pressure()
            self._overload = p.get("pressure", 0.3)
        self._emit("operator_intervention_forecasted", {"overload": self._overload})
        return {"accepted": True, "intervention_likely": self._overload > 0.6, "transparent": True}

    async def estimate_escalation_risk(self) -> dict[str, Any]:
        self._escalation = min(1.0, self._overload * 0.8)
        return {"accepted": True, "escalation": round(self._escalation, 2), "approval_gated": True}

    async def optimize_intervention_timing(self) -> dict[str, Any]:
        return {"accepted": True, "timing": "deferred", "operator_override": True}

    async def detect_operator_overload(self) -> dict[str, Any]:
        overloaded = self._overload > 0.75
        if overloaded:
            self._emit("operator_overload_detected", {"overload": self._overload})
        return {"accepted": True, "overloaded": overloaded, "operator_visible": True}

    def snapshot(self) -> dict[str, Any]:
        return {"overload": self._overload, "escalation": self._escalation}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="intervention_intelligence")
