"""Resilience manager — workflow recovery and failure domains."""

from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from odin_backend.events.bus import EventBus
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId
from odin_backend.models.workflow import WorkflowRun, WorkflowRunStatus
from odin_backend.resilience.circuit_breaker import CircuitBreaker, CircuitState
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class WorkflowCheckpoint(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    workflow_id: str
    step_index: int
    state: dict[str, Any] = Field(default_factory=dict)


class RecoveryReport(BaseModel):
    workflow_id: str
    action: str
    success: bool
    diagnostics: list[str] = Field(default_factory=list)
    degraded_mode: bool = False
    explanation: str = ""


class ResilienceManager:
    def __init__(self, event_bus: EventBus) -> None:
        self._event_bus = event_bus
        self._breakers: dict[str, CircuitBreaker] = {}
        self._checkpoints: dict[str, list[WorkflowCheckpoint]] = {}
        self._isolated_workflows: set[str] = set()

    def get_breaker(self, name: str) -> CircuitBreaker:
        if name not in self._breakers:
            self._breakers[name] = CircuitBreaker(name=name)
        return self._breakers[name]

    def record_tool_failure(self, tool_name: str) -> CircuitState:
        return self.get_breaker(f"tool:{tool_name}").record_failure()

    def record_tool_success(self, tool_name: str) -> None:
        self.get_breaker(f"tool:{tool_name}").record_success()

    def is_tool_available(self, tool_name: str) -> bool:
        return self.get_breaker(f"tool:{tool_name}").allow_request()

    def save_checkpoint(self, workflow_id: str, step_index: int, state: dict[str, Any]) -> WorkflowCheckpoint:
        cp = WorkflowCheckpoint(workflow_id=workflow_id, step_index=step_index, state=state)
        self._checkpoints.setdefault(workflow_id, []).append(cp)
        return cp

    def get_latest_checkpoint(self, workflow_id: str) -> WorkflowCheckpoint | None:
        cps = self._checkpoints.get(workflow_id, [])
        return cps[-1] if cps else None

    async def recover_workflow(
        self,
        run: WorkflowRun,
        *,
        use_degraded_path: bool = False,
    ) -> RecoveryReport:
        diagnostics: list[str] = []
        if run.status != WorkflowRunStatus.FAILED:
            diagnostics.append("Workflow not in failed state")
            return RecoveryReport(
                workflow_id=run.id,
                action="noop",
                success=False,
                diagnostics=diagnostics,
                explanation="Only failed workflows can be recovered",
            )

        if run.id in self._isolated_workflows:
            diagnostics.append("Workflow isolated in failure domain")
            return RecoveryReport(
                workflow_id=run.id,
                action="isolated",
                success=False,
                diagnostics=diagnostics,
                explanation="Workflow isolated to prevent cascade — manual review required",
            )

        cp = self.get_latest_checkpoint(run.id)
        if cp:
            diagnostics.append(f"Checkpoint available at step {cp.step_index}")
            action = "checkpoint_replay"
        elif use_degraded_path:
            diagnostics.append("Using degraded execution path")
            action = "degraded_restart"
        else:
            diagnostics.append("No checkpoint — partial restart from step 0")
            action = "partial_restart"

        report = RecoveryReport(
            workflow_id=run.id,
            action=action,
            success=True,
            diagnostics=diagnostics,
            degraded_mode=use_degraded_path,
            explanation=f"Recovery plan: {action}. Re-execution requires ODIN approval.",
        )
        await self._event_bus.publish(
            Event(
                type=EventType.RESILIENCE_RECOVERY,
                source=AgentId.ODIN,
                workflow_id=run.id,
                payload=report.model_dump(),
            )
        )
        return report

    def isolate_workflow(self, workflow_id: str) -> None:
        self._isolated_workflows.add(workflow_id)

    def breaker_status(self) -> list[dict[str, Any]]:
        return [b.model_dump() for b in self._breakers.values()]
