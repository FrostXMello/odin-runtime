"""Persistent queue item models."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class QueueItemStatus(StrEnum):
    PENDING = "pending"
    VISIBLE = "visible"
    LEASED = "leased"
    ACKED = "acked"
    DEADLETTER = "deadletter"


class QueueItem(BaseModel):
    queue_item_id: str = Field(default_factory=lambda: str(uuid4()))
    mission_id: str | None = None
    task_id: str | None = None
    execution_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    priority: int = 50
    status: QueueItemStatus = QueueItemStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    visible_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    lease_expiry: datetime | None = None
    retry_count: int = 0
    dedup_key: str | None = None
    worker_id: str | None = None
    reason: str = "scheduled"
    fencing_token: int | None = None
    lease_epoch: int = 0
    required_capability: str | None = None

    def to_row(self) -> dict[str, Any]:
        return {
            "queue_item_id": self.queue_item_id,
            "mission_id": self.mission_id,
            "task_id": self.task_id,
            "execution_id": self.execution_id,
            "payload": self.payload,
            "priority": self.priority,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "visible_at": self.visible_at.isoformat(),
            "lease_expiry": self.lease_expiry.isoformat() if self.lease_expiry else None,
            "retry_count": self.retry_count,
            "dedup_key": self.dedup_key,
            "worker_id": self.worker_id,
            "reason": self.reason,
        }

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> QueueItem:
        def _dt(v: str | None) -> datetime | None:
            if not v:
                return None
            return datetime.fromisoformat(v.replace("Z", "+00:00"))

        return cls(
            queue_item_id=row["queue_item_id"],
            mission_id=row.get("mission_id"),
            task_id=row.get("task_id"),
            execution_id=row.get("execution_id"),
            payload=row.get("payload") or {},
            priority=int(row.get("priority") or 50),
            status=QueueItemStatus(row["status"]),
            created_at=_dt(row["created_at"]) or datetime.now(timezone.utc),
            visible_at=_dt(row["visible_at"]) or datetime.now(timezone.utc),
            lease_expiry=_dt(row.get("lease_expiry")),
            retry_count=int(row.get("retry_count") or 0),
            dedup_key=row.get("dedup_key"),
            worker_id=row.get("worker_id"),
            reason=row.get("reason") or "scheduled",
        )


class DeadLetterItem(BaseModel):
    deadletter_id: str = Field(default_factory=lambda: str(uuid4()))
    queue_item_id: str
    reason: str
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    replay_count: int = 0
    mission_id: str | None = None
