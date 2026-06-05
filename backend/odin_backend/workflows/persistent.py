"""Long-running workflows — pause, resume, cancel, checkpoints."""

import json
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from odin_backend.config import Settings
from odin_backend.events.bus import EventBus
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class PersistentWorkflowStatus(StrEnum):
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class WorkflowCheckpoint(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    step_index: int
    state: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PersistentWorkflow(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    objective: str
    schedule_cron: str | None = None  # e.g. "0 9 * * *"
    status: PersistentWorkflowStatus = PersistentWorkflowStatus.SCHEDULED
    checkpoints: list[WorkflowCheckpoint] = Field(default_factory=list)
    current_step: int = 0
    requires_approval: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PersistentWorkflowEngine:
    def __init__(self, settings: Settings, event_bus: EventBus) -> None:
        self._settings = settings
        self._event_bus = event_bus
        self._workflows: dict[str, PersistentWorkflow] = {}
        self._store_path = Path("./data/persistent_workflows.json")
        self._load()

    def _load(self) -> None:
        if self._store_path.exists():
            try:
                data = json.loads(self._store_path.read_text())
                for w in data:
                    self._workflows[w["id"]] = PersistentWorkflow.model_validate(w)
            except Exception as exc:
                logger.warning("persistent_workflow_load_failed", error=str(exc))

    def _save(self) -> None:
        self._store_path.parent.mkdir(parents=True, exist_ok=True)
        self._store_path.write_text(
            json.dumps([w.model_dump(mode="json") for w in self._workflows.values()], indent=2)
        )

    def register(self, workflow: PersistentWorkflow) -> PersistentWorkflow:
        self._workflows[workflow.id] = workflow
        self._save()
        return workflow

    def get(self, workflow_id: str) -> PersistentWorkflow | None:
        return self._workflows.get(workflow_id)

    def list_all(self) -> list[PersistentWorkflow]:
        return list(self._workflows.values())

    async def pause(self, workflow_id: str) -> PersistentWorkflow | None:
        w = self._workflows.get(workflow_id)
        if not w:
            return None
        w.status = PersistentWorkflowStatus.PAUSED
        self._save()
        await self._emit(EventType.WORKFLOW_PAUSED, workflow_id)
        return w

    async def resume(self, workflow_id: str) -> PersistentWorkflow | None:
        w = self._workflows.get(workflow_id)
        if not w:
            return None
        w.status = PersistentWorkflowStatus.RUNNING
        self._save()
        await self._emit(EventType.WORKFLOW_RESUMED, workflow_id)
        return w

    async def cancel(self, workflow_id: str) -> PersistentWorkflow | None:
        w = self._workflows.get(workflow_id)
        if not w:
            return None
        w.status = PersistentWorkflowStatus.CANCELLED
        self._save()
        await self._emit(EventType.TASK_CANCELLED, workflow_id)
        return w

    async def checkpoint(self, workflow_id: str, step_index: int, state: dict) -> WorkflowCheckpoint | None:
        w = self._workflows.get(workflow_id)
        if not w:
            return None
        cp = WorkflowCheckpoint(step_index=step_index, state=state)
        w.checkpoints.append(cp)
        w.current_step = step_index
        self._save()
        await self._event_bus.publish(
            Event(
                type=EventType.WORKFLOW_CHECKPOINT,
                source=AgentId.ODIN,
                workflow_id=workflow_id,
                payload=cp.model_dump(mode="json"),
            )
        )
        return cp

    async def _emit(self, event_type: EventType, workflow_id: str) -> None:
        await self._event_bus.publish(
            Event(type=event_type, source=AgentId.ODIN, workflow_id=workflow_id)
        )
