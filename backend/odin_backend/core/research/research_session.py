"""Persistent research sessions."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class ResearchIteration(BaseModel):
    iteration: int
    hypothesis: str
    critique: str = ""
    synthesis: str = ""
    contradictions: list[dict[str, Any]] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ResearchSession(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    topic: str
    status: str = "active"
    iterations: list[ResearchIteration] = Field(default_factory=list)
    report: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
