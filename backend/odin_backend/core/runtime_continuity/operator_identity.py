"""Operator identity model for continuity."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field


class OperatorIdentity(BaseModel):
    operator_id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = "default"
    preferences: dict = Field(default_factory=dict)
    interaction_count: int = 0
    last_seen: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    collaboration_style: str = "balanced"
