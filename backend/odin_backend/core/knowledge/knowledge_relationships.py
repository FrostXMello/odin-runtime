"""Knowledge relationship models."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field


class KnowledgeRelationship(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    source_entity: str
    target_entity: str
    relation: str
    confidence: float = 0.5
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
