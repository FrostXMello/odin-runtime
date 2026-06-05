"""Tool execution trace schemas."""

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class ToolExecutionResult(BaseModel):
    """Standardized tool output — all tools return this shape."""

    success: bool
    data: dict[str, Any] = Field(default_factory=dict)
    logs: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    execution_time: float = 0.0
    trace_id: str | None = None

    def to_legacy(self):
        from odin_backend.tools.base import ToolResult

        return ToolResult(
            success=self.success,
            data=self.data,
            error=self.errors[0] if self.errors else None,
        )


class ExecutionTrace(BaseModel):
    trace_id: str = Field(default_factory=lambda: str(uuid4()))
    workflow_id: str | None = None
    task_id: str | None = None
    agent_id: str | None = None
    tool_name: str | None = None
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ended_at: datetime | None = None
    success: bool | None = None
    events: list[str] = Field(default_factory=list)
