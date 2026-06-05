"""Meta-reasoning orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.meta_reasoning.behavior_drift_detection import detect_drift
from odin_backend.core.meta_reasoning.confidence_calibration import calibrate
from odin_backend.core.meta_reasoning.hallucination_review import review
from odin_backend.core.meta_reasoning.reasoning_diagnostics import diagnose
from odin_backend.core.meta_reasoning.recursive_instability import detect
from odin_backend.core.meta_reasoning.self_analysis import analyze_quality


class MetaReasoningRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._analyses: list[dict[str, Any]] = []

    async def analyze(self, *, confidence: float = 0.7, evidence_count: int = 3) -> dict[str, Any]:
        if not getattr(self._app.settings, "meta_reasoning_enabled", False):
            return {"accepted": False, "reason": "meta_reasoning_disabled"}
        quality = analyze_quality(confidence=confidence, evidence_count=evidence_count)
        diag = diagnose(loop_depth=2, contradiction_count=1)
        cal = calibrate(predicted=confidence, actual=0.65)
        hall = review(claims=["fact_a", "fact_b", "fact_c"], evidence=["fact_a"])
        recur = detect(depth=3)
        drift = detect_drift(baseline=0.5, current=0.55)
        result = {
            "quality": quality,
            "diagnostics": diag,
            "calibration": cal,
            "hallucination": hall,
            "recursion": recur,
            "drift": drift,
            "causal_explanation": "meta_analysis_of_reasoning_pipeline",
            "uncertainty": quality["uncertainty"],
        }
        self._analyses.append(result)
        if hall["hallucination_risk"]:
            self._emit("hallucination_detected", hall)
        self._emit("meta_analysis_generated", {"confidence": confidence})
        return {"accepted": True, "analysis": result}

    def mission_analysis(self, mission_id: str) -> list[dict[str, Any]]:
        return [a for a in self._analyses if a.get("mission_id") == mission_id]

    def snapshot(self) -> dict[str, Any]:
        return {"analysis_count": len(self._analyses), "recent": self._analyses[-3:]}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="meta_reasoning")
