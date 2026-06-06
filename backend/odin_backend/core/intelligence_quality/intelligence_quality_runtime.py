"""Cognitive quality orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.intelligence_quality.chain_quality_tracker import ChainQualityTracker
from odin_backend.core.intelligence_quality.confidence_calibration import calibrate
from odin_backend.core.intelligence_quality.contradiction_reducer import reduce_contradictions
from odin_backend.core.intelligence_quality.execution_reflection import reflect_execution
from odin_backend.core.intelligence_quality.hallucination_barrier import assess_hallucination_risk
from odin_backend.core.intelligence_quality.plan_quality import score_plan
from odin_backend.core.intelligence_quality.reasoning_evaluator import evaluate_chain
from odin_backend.core.intelligence_quality.response_grader import grade_response


class IntelligenceQualityRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._chains = ChainQualityTracker()

    async def evaluate(
        self,
        *,
        text: str,
        steps: list[str] | None = None,
        plan_steps: list[dict] | None = None,
        citations: list[str] | None = None,
    ) -> dict[str, Any]:
        if not getattr(self._app.settings, "intelligence_quality_enabled", False):
            return {"accepted": False, "reason": "intelligence_quality_disabled"}
        chain = evaluate_chain(steps=steps or [text[:120]], evidence=citations)
        grade = grade_response(text=text)
        risk = assess_hallucination_risk(text=text, citations=citations)
        plan = score_plan(steps=plan_steps or []) if plan_steps else {"score": None, "valid": True}
        conf = calibrate(raw_confidence=grade["score"], quality_score=chain["score"], risk=risk["risk"])
        self._chains.record(chain["score"])
        if risk["high_risk"]:
            self._emit("hallucination_risk_detected", risk)
        self._emit("reasoning_quality_scored", {"chain": chain["score"], "grade": grade["score"], "confidence": conf["adjusted"]})
        return {
            "accepted": True,
            "chain": chain,
            "grade": grade,
            "plan": plan,
            "risk": risk,
            "confidence": conf,
            "tracker": self._chains.snapshot(),
        }

    async def reduce_memory_contradictions(self, statements: list[str]) -> dict[str, Any]:
        result = reduce_contradictions(statements=statements)
        return {"accepted": True, **result}

    async def reflect(self, *, success: bool, error: str | None = None, retries: int = 0) -> dict[str, Any]:
        return {"accepted": True, **reflect_execution(success=success, error=error, retries=retries)}

    def snapshot(self) -> dict[str, Any]:
        return {"chains": self._chains.snapshot()}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="intelligence_quality")
