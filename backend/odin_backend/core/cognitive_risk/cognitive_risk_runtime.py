"""Cognitive risk runtime (Prompt 59)."""
from __future__ import annotations
from typing import Any

RISK_CATEGORIES = ("execution", "continuity", "cognition", "coordination", "overload", "intervention")


class CognitiveRiskRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._risk = 0.25
        self._drift = 0.0
        self._sim_loops = 0

    async def forecast_cognitive_risk(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "cognitive_risk_enabled", False):
            return {"accepted": False, "reason": "cognitive_risk_disabled"}
        if hasattr(self._app, "predictive_recovery"):
            f = await self._app.predictive_recovery.forecast_execution_failure()
            self._risk = f.get("risk", 0.25)
        self._emit("cognitive_risk_forecasted", {"risk": self._risk})
        return {"accepted": True, "risk": round(self._risk, 2), "categories": list(RISK_CATEGORIES), "supervised": True}

    async def simulate_failure_chain(self) -> dict[str, Any]:
        if self._sim_loops > 36:
            return {"accepted": False, "reason": "simulation_bounded"}
        self._sim_loops += 1
        chain = ["blocker", "interruption", "recovery"]
        self._emit("failure_chain_simulated", {"steps": len(chain)})
        return {"accepted": True, "chain": chain, "approval_gated": True}

    async def compute_risk_surface(self) -> dict[str, Any]:
        surface = {c: round(self._risk * 0.8, 2) for c in RISK_CATEGORIES}
        return {"accepted": True, "surface": surface, "transparent": True}

    async def detect_governance_drift(self) -> dict[str, Any]:
        self._drift = min(1.0, self._drift + 0.02)
        drifted = self._drift > 0.2
        if drifted:
            self._emit("governance_drift_detected", {"drift": self._drift})
        return {"accepted": True, "drift": round(self._drift, 3), "drifted": drifted}

    def snapshot(self) -> dict[str, Any]:
        return {"risk": self._risk, "drift": self._drift}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="cognitive_risk")
