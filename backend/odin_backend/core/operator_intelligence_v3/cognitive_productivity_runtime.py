"""Operator intelligence & productivity V3 (Prompt 50)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.operator_intelligence_v3.adaptive_workflow_mentor import AdaptiveWorkflowMentor
from odin_backend.core.operator_intelligence_v3.burnout_awareness_runtime import BurnoutAwarenessRuntime
from odin_backend.core.operator_intelligence_v3.cognitive_recovery_planner import plan as recovery_plan
from odin_backend.core.operator_intelligence_v3.deep_focus_coordinator import DeepFocusCoordinator
from odin_backend.core.operator_intelligence_v3.strategy_recommendation_engine import recommend


class CognitiveProductivityRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._burnout = BurnoutAwarenessRuntime(app)
        self._focus = DeepFocusCoordinator(app)
        self._mentor = AdaptiveWorkflowMentor(app)

    async def optimize(self, *, hours: float = 4.0, context: str = "engineering") -> dict[str, Any]:
        if not getattr(self._app.settings, "operator_intelligence_v3_enabled", False):
            return {"accepted": False, "reason": "operator_intelligence_v3_disabled"}
        burnout = await self._burnout.assess(hours=hours)
        strategy = recommend(fatigue=burnout.get("burnout_risk", False))
        recovery = recovery_plan(fatigue=burnout.get("burnout_risk", False))
        workflow = await self._mentor.recommend(context=context)
        return {
            "accepted": True,
            "burnout": burnout,
            "strategy": strategy,
            "recovery": recovery,
            "workflow": workflow,
            "local_only": True,
            "operator_override": True,
        }

    async def start_deep_focus(self, *, minutes: int = 45) -> dict[str, Any]:
        return await self._focus.start(minutes=minutes)

    def snapshot(self) -> dict[str, Any]:
        return {"focus": self._focus.snapshot()}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="operator_intelligence_v3")
