"""Proactive assistance runtime (Prompt 48)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.proactive_assistance.attention_intervention import safe_intervene
from odin_backend.core.proactive_assistance.contextual_assistance import contextualize
from odin_backend.core.proactive_assistance.interruption_scoring import score
from odin_backend.core.proactive_assistance.suggestion_priority import prioritize
from odin_backend.core.proactive_assistance.timing_prediction import predict_idle
from odin_backend.core.proactive_assistance.workflow_assistance import hint


class ProactiveAssistanceRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app

    async def evaluate(self, *, context: str = "", idle_s: float = 0.0, urgency: float = 0.5) -> dict[str, Any]:
        if not getattr(self._app.settings, "proactive_assistance_runtime_enabled", False):
            return {"accepted": False, "reason": "proactive_assistance_runtime_disabled"}
        s = score(urgency=urgency, operator_busy=idle_s < 10)
        if not safe_intervene(score=s):
            return {"accepted": True, "intervention": False, "reason": "attention_safe_hold"}
        if not predict_idle(idle_s=idle_s) and urgency < 0.8:
            return {"accepted": True, "intervention": False, "reason": "not_idle"}
        h = hint(workflow=context or "engineering")
        ctx = await contextualize(self._app, context=context)
        suggestions = prioritize([{"priority": s, **h}])
        self._emit("assistance_intervention_generated", {"count": len(suggestions)})
        return {
            "accepted": True,
            "intervention": True,
            "suggestions": suggestions,
            "context": ctx,
            "operator_controlled": True,
            "non_invasive": True,
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
        obs.tracer.record(kind, message=kind_name, payload=payload, component="proactive_assistance")
