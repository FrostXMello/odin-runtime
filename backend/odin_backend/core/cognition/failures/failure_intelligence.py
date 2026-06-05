"""Failure intelligence reports."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from odin_backend.core.cognition.failures.anomaly_detection import detect_anomalies
from odin_backend.core.cognition.failures.escalation_engine import recommend_escalation
from odin_backend.core.cognition.failures.failure_classifier import classify_failure
from odin_backend.core.cognition.failures.regression_detector import detect_regression


@dataclass
class FailureIntelligenceReport:
    root_causes: list[str] = field(default_factory=list)
    probable_fixes: list[str] = field(default_factory=list)
    recurring_bottlenecks: list[str] = field(default_factory=list)
    degraded_capabilities: list[str] = field(default_factory=list)
    anomalies: list[dict[str, Any]] = field(default_factory=list)
    regressions: list[dict[str, Any]] = field(default_factory=list)
    oscillation_detected: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "root_causes": self.root_causes,
            "probable_fixes": self.probable_fixes,
            "recurring_bottlenecks": self.recurring_bottlenecks,
            "degraded_capabilities": self.degraded_capabilities,
            "anomalies": self.anomalies,
            "regressions": self.regressions,
            "oscillation_detected": self.oscillation_detected,
        }


class FailureIntelligence:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._oscillation: dict[str, int] = {}
        self._baselines: dict[str, dict[str, float]] = {}

    def record_adaptation(self, mission_id: str, action: str) -> None:
        if action in ("retry", "replan"):
            self._oscillation[mission_id] = self._oscillation.get(mission_id, 0) + 1

    async def analyze(self, *, mission_id: str | None = None) -> FailureIntelligenceReport:
        report = FailureIntelligenceReport()
        exp = getattr(self._app, "experience_engine", None)
        intel = getattr(self._app, "execution_intelligence", None)
        retrieval = getattr(self._app, "memory_retrieval", None)

        metrics: dict[str, Any] = {}
        if exp:
            stats = exp.strategy_stats()
            if stats:
                rates = [s.get("success_rate", 0.5) for s in stats.values()]
                metrics["failure_rate"] = 1.0 - (sum(rates) / len(rates))
            events = getattr(exp, "_events", [])
            if events:
                metrics["retry_rate"] = sum(1 for e in events if not e.get("success")) / len(events)
            else:
                metrics["retry_rate"] = 0.0

        if intel:
            for cap, score in intel.capability_scores().items():
                if score.get("failure_rate", 0) > 0.45:
                    report.degraded_capabilities.append(cap)

        if retrieval:
            patterns = await retrieval.failure_patterns(limit=5)
            for p in patterns:
                report.recurring_bottlenecks.append(p.get("label", "")[:80])

        report.anomalies = detect_anomalies(metrics)
        if mission_id and self._oscillation.get(mission_id, 0) >= 4:
            report.oscillation_detected = True
            report.root_causes.append("mission_oscillation: retry/replan loop")
            rec = recommend_escalation(
                classify_failure(reason="oscillation", execution_state="failed", retry_count=3),
                oscillation=True,
            )
            report.probable_fixes.extend(rec["probable_fixes"])

        if intel and self._baselines.get("capabilities"):
            report.regressions = detect_regression(
                {k: v.get("reliability", 0) for k, v in intel.capability_scores().items()},
                self._baselines["capabilities"],
            )

        if report.anomalies:
            self._emit("failure_pattern_detected", report.to_dict())

        return report

    def set_capability_baseline(self) -> None:
        intel = getattr(self._app, "execution_intelligence", None)
        if intel:
            self._baselines["capabilities"] = {
                k: v.get("reliability", 0.5) for k, v in intel.capability_scores().items()
            }

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="failure_intelligence")
