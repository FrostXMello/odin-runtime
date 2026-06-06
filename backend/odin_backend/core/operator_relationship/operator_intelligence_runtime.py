"""Operator intelligence orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.knowledge.research_quality import (
    citation_quality,
    decay_score,
    long_horizon_plan,
    resolve_contradiction,
    score_source,
    track_topic,
    validate_synthesis,
)
from odin_backend.core.operator_relationship.operator_intelligence import (
    build_operator_context,
    infer_project_priority,
    interruption_allowed,
    learn_habit,
    predict_intent,
    predict_workflow,
)


class OperatorIntelligenceRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._history: list[str] = []

    async def infer(self, *, signals: list[str] | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "operator_intelligence_enabled", False):
            return {"accepted": False, "reason": "operator_intelligence_disabled"}
        signals = signals or self._history[-20:]
        intent = predict_intent(signals=signals)
        workflow = predict_workflow(history=signals)
        ctx = build_operator_context(active_app=signals[-1] if signals else "unknown", project=None, idle_minutes=0)
        projects = []
        if hasattr(self._app, "project_os"):
            projects = infer_project_priority(self._app.project_os._registry.list_all())
        suggestion = None
        if projects:
            suggestion = f"Resume {projects[0].get('name', 'project')} work?"
        self._emit("operator_intent_inferred", {"intent": intent["intent"], "confidence": intent["confidence"]})
        return {"accepted": True, "intent": intent, "workflow": workflow, "context": ctx, "suggestion": suggestion}

    async def validate_research(self, *, claims: list[str], sources: list[str]) -> dict[str, Any]:
        result = validate_synthesis(claims=claims, sources=sources)
        cites = citation_quality(citations=sources)
        if result["valid"]:
            self._emit("synthesis_validated", {"claims": len(claims), "sources": len(sources)})
        return {"accepted": True, "synthesis": result, "citations": cites}

    async def research_topic(self, *, topic: str) -> dict[str, Any]:
        plan = long_horizon_plan(topic=topic)
        tracked = track_topic(topic=topic, updates=[topic])
        return {"accepted": True, "plan": plan, "topic": tracked}

    def record_action(self, action: str) -> None:
        self._history.append(action)

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
        obs.tracer.record(kind, message=kind_name, payload=payload, component="operator_intelligence")
