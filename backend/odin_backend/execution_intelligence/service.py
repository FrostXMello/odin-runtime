"""Execution intelligence service — analytics and adaptive recommendations."""

from typing import Any

from odin_backend.events.bus import EventBus
from odin_backend.execution_intelligence.reliability import ToolReliabilityTracker
from odin_backend.execution_intelligence.strategies import ExecutionStrategySelector
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId
from odin_backend.models.workflow import WorkflowRun
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class ExecutionIntelligenceService:
    def __init__(self, event_bus: EventBus) -> None:
        self._event_bus = event_bus
        self._tracker = ToolReliabilityTracker()
        self._selector = ExecutionStrategySelector()

    def record_tool_execution(
        self,
        tool_name: str,
        *,
        success: bool,
        latency_ms: float = 0.0,
        domain: str = "general",
    ) -> None:
        self._tracker.record(tool_name, success=success, latency_ms=latency_ms, domain=domain)

    def get_reliability_scores(self) -> list[dict[str, Any]]:
        return [s.model_dump() for s in self._tracker.all_scores()]

    def recommend_for_tool(self, tool_name: str, domain: str = "general") -> dict[str, Any]:
        scores = self._tracker.all_scores()
        selected, reason = self._selector.select_tool(tool_name, scores)
        score = self._tracker.score(tool_name, domain)
        recs: list[str] = []
        if reason:
            recs.append(reason)
        if score.sample_size >= 3 and score.success_rate < 0.6:
            recs.append(f"Tool reliability degraded for domain '{domain}' ({score.success_rate:.0%}).")
        return {
            "preferred_tool": tool_name,
            "recommended_tool": selected,
            "reliability": score.model_dump(),
            "recommendations": recs,
            "explainable": {
                "sample_size": score.sample_size,
                "success_rate": score.success_rate,
                "fallback_triggered": selected != tool_name,
            },
        }

    async def analyze_workflow(self, run: WorkflowRun) -> dict[str, Any]:
        bottlenecks = self._selector.analyze_bottlenecks(run.step_results)
        recs: list[str] = list(bottlenecks)
        parallel_hint = self._selector.recommend_parallelization(
            len(run.step_results),
            sum(
                r.get("latency_ms", 0)
                for r in run.step_results.values()
                if isinstance(r, dict)
            )
            / max(len(run.step_results), 1),
        )
        if parallel_hint:
            recs.append(parallel_hint)

        for r in run.step_results.values():
            if isinstance(r, dict) and r.get("tool"):
                self.record_tool_execution(
                    r["tool"],
                    success=bool(r.get("success")),
                    latency_ms=float(r.get("latency_ms", 0)),
                )

        report = {
            "workflow_id": run.id,
            "bottlenecks": bottlenecks,
            "recommendations": recs or ["No optimization issues detected."],
            "reliability_scores": self.get_reliability_scores(),
        }
        await self._event_bus.publish(
            Event(
                type=EventType.EXECUTION_INTELLIGENCE_UPDATED,
                source=AgentId.ODIN,
                workflow_id=run.id,
                payload=report,
            )
        )
        return report
