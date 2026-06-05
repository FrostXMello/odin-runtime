"""Task domain schemas — central unit of work delegation."""

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class AgentId(StrEnum):
    """Registered specialized agents."""

    ODIN = "odin"
    VALKYRIE = "valkyrie"
    MIMIR = "mimir"
    HUGIN = "hugin"
    MUNIN = "munin"
    FAFNIR = "fafnir"
    BROKK = "brokk"
    HEIMDALL = "heimdall"
    FREYA = "freya"
    BRAGI = "bragi"


class TaskStatus(StrEnum):
    PENDING = "pending"
    QUEUED = "queued"
    ASSIGNED = "assigned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(StrEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TaskCreate(BaseModel):
    """Payload to create a new task."""

    title: str
    description: str = ""
    assigned_agent: AgentId | None = None
    parent_task_id: str | None = None
    workflow_id: str | None = None
    priority: TaskPriority = TaskPriority.NORMAL
    payload: dict[str, Any] = Field(default_factory=dict)
    required_tools: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    timeout_seconds: int | None = None


class TaskUpdate(BaseModel):
    """Partial task update."""

    status: TaskStatus | None = None
    assigned_agent: AgentId | None = None
    result: dict[str, Any] | None = None
    error: str | None = None
    metadata: dict[str, Any] | None = None


class TaskResult(BaseModel):
    """Structured agent execution result."""

    success: bool
    output: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    artifacts: list[str] = Field(default_factory=list)
    duration_ms: int | None = None


class Task(BaseModel):
    """Full task entity."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.NORMAL
    assigned_agent: AgentId | None = None
    created_by: AgentId = AgentId.ODIN
    parent_task_id: str | None = None
    workflow_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    required_tools: list[str] = Field(default_factory=list)
    result: TaskResult | None = None
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    timeout_seconds: int | None = None
    created_at: datetime = Field(default_factory=_utc_now)
    updated_at: datetime = Field(default_factory=_utc_now)
    started_at: datetime | None = None
    completed_at: datetime | None = None

    def touch(self) -> None:
        self.updated_at = _utc_now()

    def mark_running(self, agent: AgentId) -> None:
        self.status = TaskStatus.RUNNING
        self.assigned_agent = agent
        self.started_at = _utc_now()
        self.touch()

    def mark_completed(self, result: TaskResult) -> None:
        self.status = TaskStatus.COMPLETED
        self.result = result
        self.completed_at = _utc_now()
        self.touch()

    def mark_failed(self, error: str) -> None:
        self.status = TaskStatus.FAILED
        self.error = error
        self.completed_at = _utc_now()
        self.touch()
