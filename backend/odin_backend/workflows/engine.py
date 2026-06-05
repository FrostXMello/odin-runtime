"""Workflow engine — orchestrates multi-step task sequences."""

from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from odin_backend.events.bus import EventBus
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId, TaskCreate
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class WorkflowStep(BaseModel):
    name: str
    task_create: TaskCreate
    depends_on: list[str] = Field(default_factory=list)


class Workflow(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str = ""
    steps: list[WorkflowStep]
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkflowEngine:
    """Triggers and tracks workflow execution via orchestrator."""

    def __init__(self, event_bus: EventBus) -> None:
        self._event_bus = event_bus
        self._workflows: dict[str, Workflow] = {}

    def register(self, workflow: Workflow) -> None:
        self._workflows[workflow.id] = workflow

    async def trigger(self, workflow_id: str) -> list[TaskCreate]:
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Unknown workflow: {workflow_id}")

        await self._event_bus.publish(
            Event(
                type=EventType.WORKFLOW_TRIGGERED,
                source=AgentId.ODIN,
                workflow_id=workflow_id,
                payload={"name": workflow.name},
            )
        )

        task_creates: list[TaskCreate] = []
        for step in workflow.steps:
            tc = step.task_create.model_copy(
                update={"workflow_id": workflow_id, "metadata": {**step.task_create.metadata, "step": step.name}}
            )
            task_creates.append(tc)

        logger.info("workflow_triggered", workflow_id=workflow_id, steps=len(task_creates))
        return task_creates
