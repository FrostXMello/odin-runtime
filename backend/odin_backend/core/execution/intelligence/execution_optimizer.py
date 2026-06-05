"""Execution optimization coordinator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.execution.intelligence.adaptive_timeout import estimate_timeout
from odin_backend.core.execution.intelligence.capability_performance import CapabilityPerformanceTracker
from odin_backend.core.execution.intelligence.execution_profiler import ExecutionProfiler
from odin_backend.core.execution.intelligence.retry_intelligence import retry_delay, should_replan_instead_of_retry
from odin_backend.execution_intelligence.service import ExecutionIntelligenceService


class ExecutionIntelligence:
    def __init__(self, app: Any | None = None, *, legacy_service: Any | None = None) -> None:
        self._app = app
        self._legacy_service = legacy_service
        self._capabilities = CapabilityPerformanceTracker()
        self._profiler = ExecutionProfiler()
        event_bus = getattr(app, "event_bus", None)
        self._legacy = ExecutionIntelligenceService(event_bus) if event_bus else None

    def capability_scores(self) -> dict[str, dict[str, Any]]:
        return self._capabilities.scores()

    def record_execution(
        self,
        capability: str,
        *,
        success: bool,
        latency_ms: float | None = None,
        execution_id: str | None = None,
    ) -> None:
        self._capabilities.record(capability, success=success, latency_ms=latency_ms)
        if execution_id:
            self._profiler.update(execution_id, capability=capability, success=success, latency_ms=latency_ms)
    def suggest_timeout(self, capability: str, *, base: float = 120.0) -> float:
        scores = self._capabilities.scores().get(capability, {})
        return estimate_timeout(
            capability,
            base_seconds=base,
            avg_latency_ms=scores.get("avg_latency_ms"),
            failure_rate=scores.get("failure_rate", 0),
        )

    def suggest_retry_delay(
        self,
        *,
        attempt: int,
        capability: str,
        plan_confidence: float = 0.75,
        base: float = 2.0,
    ) -> float:
        fr = self._capabilities.scores().get(capability, {}).get("failure_rate", 0)
        return retry_delay(attempt=attempt, base_seconds=base, failure_rate=fr, plan_confidence=plan_confidence)

    def route_score(self, capability: str, worker_load: float = 0.0) -> float:
        scores = self._capabilities.scores().get(capability, {})
        reliability = scores.get("reliability", 0.5)
        return reliability * 100.0 - worker_load * 20.0

    def replan_recommended(
        self,
        *,
        attempt: int,
        max_retries: int,
        oscillation_score: int,
        capability: str,
    ) -> bool:
        fr = self._capabilities.scores().get(capability, {}).get("failure_rate", 0)
        return should_replan_instead_of_retry(
            attempt=attempt,
            max_retries=max_retries,
            failure_rate=fr,
            oscillation_score=oscillation_score,
        )

    @property
    def profiler(self) -> ExecutionProfiler:
        return self._profiler

    def record_tool_execution(
        self,
        tool_name: str,
        *,
        success: bool,
        latency_ms: float = 0.0,
        domain: str = "general",
    ) -> None:
        if self._legacy_service is not None:
            self._legacy_service.record_tool_execution(
                tool_name,
                success=success,
                latency_ms=latency_ms,
                domain=domain,
            )

    def get_reliability_scores(self) -> list[dict[str, Any]]:
        if self._legacy_service is not None:
            return self._legacy_service.get_reliability_scores()
        return []

    def recommend_for_tool(self, tool_name: str, domain: str = "general") -> dict[str, Any]:
        if self._legacy_service is not None:
            return self._legacy_service.recommend_for_tool(tool_name, domain=domain)
        return {"preferred_tool": tool_name, "recommended_tool": tool_name, "recommendations": []}
