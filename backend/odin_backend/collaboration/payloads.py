"""Shared context payloads for inter-agent collaboration."""

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from odin_backend.models.task import AgentId


class SharedContextPayload(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    chain_id: str
    from_agent: AgentId
    to_agent: AgentId
    artifact_type: str  # analysis | data | sub_result | request
    content: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CollaborationChain(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    objective: str
    steps: list[dict[str, str]] = Field(default_factory=list)
    payloads: list[SharedContextPayload] = Field(default_factory=list)
    status: str = "pending"  # pending | running | completed | failed
    final_result: dict[str, Any] | None = None
