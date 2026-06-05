"""Persistent agent identity model."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class AgentIdentity(BaseModel):
    agent_id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    role: str = "generalist"
    capabilities: list[str] = Field(default_factory=list)
    confidence: float = 0.5
    expertise_domains: list[str] = Field(default_factory=list)
    collaboration_preferences: list[str] = Field(default_factory=list)
    communication_style: str = "analytical"
    long_term_objectives: list[str] = Field(default_factory=list)
    reasoning_tendencies: list[str] = Field(default_factory=list)
    status: str = "active"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)
