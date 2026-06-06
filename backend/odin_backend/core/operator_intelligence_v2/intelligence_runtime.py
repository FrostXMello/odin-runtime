"""Operator intelligence V2 (Prompt 49)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.operator_intelligence_v2.adaptive_assistance_runtime import AdaptiveAssistanceRuntime
from odin_backend.core.operator_intelligence_v2.cognitive_fatigue_detector import detect
from odin_backend.core.operator_intelligence_v2.operator_behavior_model import OperatorBehaviorModel
from odin_backend.core.operator_intelligence_v2.productivity_strategy_runtime import strategy
from odin_backend.core.operator_intelligence_v2.workflow_pattern_analyzer import analyze


class OperatorIntelligenceV2Runtime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._behavior = OperatorBehaviorModel()
        self._assistance = AdaptiveAssistanceRuntime(app)

    async def analyze(self, *, hours: float = 4.0, switches: int = 3) -> dict[str, Any]:
        if not getattr(self._app.settings, "operator_intelligence_v2_enabled", False):
            return {"accepted": False, "reason": "operator_intelligence_v2_disabled"}
        obs = self._behavior.observe()
        patterns = analyze(switches=switches)
        fatigue = detect(hours=hours)
        if fatigue.get("fatigued"):
            self._emit("cognitive_fatigue_detected", fatigue)
        strat = await strategy(self._app)
        assist = await self._assistance.adjust(fatigue=fatigue.get("fatigued", False))
        return {
            "accepted": True,
            "behavior": obs,
            "patterns": patterns,
            "fatigue": fatigue,
            "strategy": strat,
            "assistance": assist,
            "local_only": True,
            "operator_controlled": True,
        }

    def snapshot(self) -> dict[str, Any]:
        return {"enabled": True}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="operator_intelligence_v2")
