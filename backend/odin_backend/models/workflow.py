"""Workflow plan schemas — structured LLM output, never raw execution."""

from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from odin_backend.models.task import AgentId


class StepStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowPlanStep(BaseModel):
    step_id: int
    agent: AgentId
    tool: str
    description: str = ""
    params: dict[str, Any] = Field(default_factory=dict)
    status: StepStatus = StepStatus.PENDING
    depends_on: list[int] = Field(default_factory=list)
    output_key: str | None = None


class WorkflowPlan(BaseModel):
    """Deterministic execution plan produced by reasoning engine."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    objective: str
    steps: list[WorkflowPlanStep]
    metadata: dict[str, Any] = Field(default_factory=dict)
    correlation_id: str | None = None

    def to_task_payloads(self) -> list[dict[str, Any]]:
        return [
            {
                "step_id": s.step_id,
                "agent": s.agent.value,
                "tool": s.tool,
                "params": s.params,
                "description": s.description,
            }
            for s in self.steps
        ]


class WorkflowRunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowRun(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    plan_id: str
    objective: str
    status: WorkflowRunStatus = WorkflowRunStatus.PENDING
    current_step: int = 0
    step_results: dict[int, dict[str, Any]] = Field(default_factory=dict)
    error: str | None = None
    trace_id: str = Field(default_factory=lambda: str(uuid4()))
