"""Knowledge node models."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class KnowledgeNode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    entity: str
    fact: str
    confidence: float = 0.5
    source: str = "local"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    supporting_evidence: list[str] = Field(default_factory=list)
    contradicting_evidence: list[str] = Field(default_factory=list)
    mission_origin: str | None = None
    reasoning_chain: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
