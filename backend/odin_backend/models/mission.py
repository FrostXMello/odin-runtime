"""Persistent mission domain models."""

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from odin_backend.models.task_graph import TaskGraph, TaskNode


class MissionLifecycle(StrEnum):
    """Strict orchestration lifecycle (legacy aliases retained for DB migration)."""

    QUEUED = "queued"
    PLANNING = "planning"
    PLANNED = "planned"
    DISPATCHED = "dispatched"
    RUNNING = "running"
    BLOCKED = "blocked"
    RETRYING = "retrying"
    ESCALATED = "escalated"
    APPROVAL_REQUIRED = "approval_required"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"
    # Legacy (migrated on load)
    CREATED = "created"
    ACTIVE = "active"
    WAITING = "waiting"


TERMINAL_MISSION_STATES = frozenset(
    {
        MissionLifecycle.COMPLETED,
        MissionLifecycle.FAILED,
        MissionLifecycle.CANCELLED,
        MissionLifecycle.ARCHIVED,
    }
)


class MissionCheckpoint(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    label: str = "wave"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    state: MissionLifecycle
    task_graph: dict[str, Any] = Field(default_factory=dict)
    reasoning_snapshot: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class MissionTaskRef(BaseModel):
    task_id: str
    goal: str
    status: str = "pending"
    wave: int = 0
    retry_count: int = 0


class Mission(BaseModel):
    """Durable long-horizon objective container."""

    mission_id: str = Field(default_factory=lambda: str(uuid4()))
    objective: str
    priority: int = Field(default=50, ge=0, le=100)
    autonomy_level: int = Field(default=1, ge=0, le=5)
    created_by: str = "user"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    current_state: MissionLifecycle = MissionLifecycle.CREATED

    active_tasks: list[MissionTaskRef] = Field(default_factory=list)
    completed_tasks: list[MissionTaskRef] = Field(default_factory=list)
    blocked_tasks: list[MissionTaskRef] = Field(default_factory=list)

    execution_history: list[dict[str, Any]] = Field(default_factory=list)
    reasoning_log: list[dict[str, Any]] = Field(default_factory=list)
    memory_refs: list[str] = Field(default_factory=list)
    graph_refs: list[str] = Field(default_factory=list)
    escalation_events: list[dict[str, Any]] = Field(default_factory=list)
    checkpoints: list[MissionCheckpoint] = Field(default_factory=list)

    task_graph: TaskGraph = Field(default_factory=TaskGraph)
    current_wave: int = 0
    retry_count: int = 0
    max_retries: int = 3
    human_approved: bool = False
    pause_reason: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    adaptation_log: list[dict[str, Any]] = Field(default_factory=list)
    execution_strategy: str = "default"
    confidence: dict[str, float] = Field(
        default_factory=lambda: {
            "execution": 0.85,
            "environment": 0.8,
            "stability": 0.85,
        }
    )

    def append_adaptation(self, action: str, *, reason: str, detail: dict | None = None) -> None:
        self.adaptation_log.append(
            {
                "action": action,
                "reason": reason,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                **(detail or {}),
            }
        )
        if len(self.adaptation_log) > 200:
            self.adaptation_log = self.adaptation_log[-200:]

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)

    def is_terminal(self) -> bool:
        from odin_backend.core.missions.lifecycle import migrate_legacy_state, TERMINAL_MISSION_STATES

        return migrate_legacy_state(self.current_state) in TERMINAL_MISSION_STATES

    @property
    def fingerprint_digest(self) -> str | None:
        return self.metadata.get("fingerprint_digest")

    def sync_task_lists(self) -> None:
        """Rebuild active/completed/blocked from embedded task graph."""
        from odin_backend.models.task_graph import TaskNodeStatus

        active: list[MissionTaskRef] = []
        completed: list[MissionTaskRef] = []
        blocked: list[MissionTaskRef] = []
        for node in self.task_graph.nodes.values():
            ref = MissionTaskRef(
                task_id=node.id,
                goal=node.goal,
                status=node.status.value,
                wave=int(node.output.get("wave", self.current_wave)),
                retry_count=node.retry_count,
            )
            if node.status == TaskNodeStatus.COMPLETE:
                completed.append(ref)
            elif node.status in (TaskNodeStatus.BLOCKED, TaskNodeStatus.FAILED):
                blocked.append(ref)
            else:
                active.append(ref)
        self.active_tasks = active
        self.completed_tasks = completed
        self.blocked_tasks = blocked

    def append_history(self, event: str, payload: dict[str, Any] | None = None) -> None:
        self.execution_history.append(
            {
                "event": event,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                **(payload or {}),
            }
        )
        if len(self.execution_history) > 500:
            self.execution_history = self.execution_history[-500:]

    def append_reasoning(self, message: str, *, detail: dict[str, Any] | None = None) -> None:
        entry = {
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **(detail or {}),
        }
        self.reasoning_log.append(entry)
        if len(self.reasoning_log) > 300:
            self.reasoning_log = self.reasoning_log[-300:]
