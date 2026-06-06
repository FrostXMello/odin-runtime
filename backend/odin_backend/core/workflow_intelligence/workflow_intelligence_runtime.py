"""Workflow intelligence orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.workflow_intelligence.engineering_habit_model import learn_habit
from odin_backend.core.workflow_intelligence.productivity_patterns import detect_patterns
from odin_backend.core.workflow_intelligence.proactive_assistance_engine import proactive_hint
from odin_backend.core.workflow_intelligence.session_prediction import predict_session
from odin_backend.core.workflow_intelligence.workflow_efficiency_analysis import analyze_efficiency
from odin_backend.core.workflow_intelligence.workflow_learning import record_workflow


class WorkflowIntelligenceRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._history: list[str] = []

    async def learn(self, *, action: str, hour: int = 12) -> dict[str, Any]:
        if not getattr(self._app.settings, "workflow_intelligence_enabled", False):
            return {"accepted": False, "reason": "workflow_intelligence_disabled"}
        self._history.append(action)
        record_workflow(action=action)
        habit = learn_habit(action=action, hour=hour)
        patterns = detect_patterns(history=self._history[-50:])
        return {"accepted": True, "habit": habit, "patterns": patterns}

    async def predict(self) -> dict[str, Any]:
        prediction = predict_session(history=self._history[-20:])
        hint = proactive_hint(prediction=prediction)
        efficiency = analyze_efficiency(session_hours=3.0)
        self._emit("workflow_predicted", prediction)
        return {"accepted": True, "prediction": prediction, "hint": hint, "efficiency": efficiency}

    def snapshot(self) -> dict[str, Any]:
        return {"history": len(self._history)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="workflow_intelligence")
