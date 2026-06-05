"""Post-workflow reflection and adaptive recommendations."""

from typing import Any

from pydantic import BaseModel, Field

from odin_backend.events.bus import EventBus
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId
from odin_backend.models.workflow import WorkflowRun, WorkflowRunStatus
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class ReflectionReport(BaseModel):
    workflow_id: str
    success: bool
    findings: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    metrics: dict[str, Any] = Field(default_factory=dict)


class ReflectionEngine:
    def __init__(self, event_bus: EventBus) -> None:
        self._event_bus = event_bus
        self._reports: dict[str, ReflectionReport] = {}

    async def reflect_on_workflow(self, run: WorkflowRun) -> ReflectionReport:
        findings: list[str] = []
        recommendations: list[str] = []

        failed_steps = [
            sid for sid, r in run.step_results.items() if not r.get("success", True)
        ]
        if failed_steps:
            findings.append(f"Steps failed: {failed_steps}")
            recommendations.append("Consider retry with alternative tools or agents.")

        if run.status == WorkflowRunStatus.FAILED:
            findings.append(f"Workflow failed: {run.error or 'unknown'}")
            recommendations.append("Review Heimdall permissions and tool availability.")

        success_count = sum(1 for r in run.step_results.values() if r.get("success"))
        total = len(run.step_results)
        if total and success_count < total:
            findings.append(f"Partial success: {success_count}/{total} steps")

        tool_counts: dict[str, int] = {}
        for r in run.step_results.values():
            for k in r.keys():
                if k not in ("success", "data", "errors", "output"):
                    tool_counts[k] = tool_counts.get(k, 0) + 1

        report = ReflectionReport(
            workflow_id=run.id,
            success=run.status == WorkflowRunStatus.COMPLETED,
            findings=findings or ["Workflow completed without notable issues."],
            recommendations=recommendations or ["No changes recommended."],
            metrics={"steps_total": total, "steps_success": success_count},
        )
        self._reports[run.id] = report

        await self._event_bus.publish(
            Event(
                type=EventType.REFLECTION_COMPLETED,
                source=AgentId.ODIN,
                workflow_id=run.id,
                payload=report.model_dump(mode="json"),
            )
        )
        return report

    def get_report(self, workflow_id: str) -> ReflectionReport | None:
        return self._reports.get(workflow_id)
