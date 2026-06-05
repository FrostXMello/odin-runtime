"""Distributed tracing correlation IDs."""

from uuid import uuid4

from pydantic import BaseModel, Field


class TraceContext(BaseModel):
    """Correlation envelope for workflows, tasks, and tools."""

    trace_id: str = Field(default_factory=lambda: str(uuid4()))
    workflow_id: str | None = None
    task_id: str | None = None
    execution_id: str = Field(default_factory=lambda: str(uuid4()))
    correlation_id: str | None = None
    parent_trace_id: str | None = None

    def child(self, **kwargs) -> "TraceContext":
        data = self.model_dump()
        data.update(kwargs)
        data["parent_trace_id"] = self.trace_id
        data["execution_id"] = str(uuid4())
        return TraceContext(**data)
