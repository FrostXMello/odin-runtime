"""Typed execution records and requests."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class ExecutionState(StrEnum):
    QUEUED = "queued"
    ALLOCATED = "allocated"
    RUNNING = "running"
    WAITING = "waiting"
    RETRYING = "retrying"
    ROLLING_BACK = "rolling_back"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"


class ExecutionType(StrEnum):
    PYTHON = "python"
    SHELL = "shell"
    WORKFLOW = "workflow"
    FILE = "file"


class ExecutionRecord(BaseModel):
    execution_id: str = Field(default_factory=lambda: str(uuid4()))
    mission_id: str | None = None
    task_id: str | None = None
    executor_agent: str = "brokk"
    capability_used: str = ""
    execution_type: ExecutionType = ExecutionType.PYTHON
    state: ExecutionState = ExecutionState.QUEUED
    lease_expiry: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: datetime | None = None
    ended_at: datetime | None = None
    retry_count: int = 0
    max_retries: int = 3
    rollback_reference: str | None = None
    stdout_ref: str = ""
    stderr_ref: str = ""
    exit_code: int | None = None
    error: str | None = None
    params: dict[str, Any] = Field(default_factory=dict)
    result: dict[str, Any] = Field(default_factory=dict)
    trace_id: str | None = None
    last_heartbeat_at: datetime | None = None
    fencing_token: int | None = None
    worker_id: str | None = None
    pool_name: str | None = None

    def touch_heartbeat(self) -> None:
        self.last_heartbeat_at = datetime.now(timezone.utc)


class ExecutionRunRequest(BaseModel):
    capability: str
    mission_id: str | None = None
    task_id: str | None = None
    executor_agent: str = "brokk"
    execution_type: ExecutionType | None = None
    params: dict[str, Any] = Field(default_factory=dict)
    timeout_seconds: float | None = None
    max_retries: int | None = None
