"""Semantic memory entries for planner context."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class SemanticMemoryEntry(BaseModel):
    entry_id: str = Field(default_factory=lambda: str(uuid4()))
    mission_id: str | None = None
    text: str
    kind: str = "outcome"  # outcome | strategy | tool | failure
    score: float = 0.5
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
