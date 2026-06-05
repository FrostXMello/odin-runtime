"""Execution snapshots for rollback metadata."""

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class ExecutionSnapshot(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    tool_name: str
    before_state: dict[str, Any] = Field(default_factory=dict)
    after_state: dict[str, Any] = Field(default_factory=dict)
    diff_summary: str = ""
    rollback_available: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
