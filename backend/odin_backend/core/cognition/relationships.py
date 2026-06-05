"""Memory graph relationship types."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class RelationshipType(StrEnum):
    CAUSED_FAILURE = "caused_failure"
    SOLVED_BY = "solved_by"
    DEPENDS_ON = "depends_on"
    SIMILAR_TO = "similar_to"
    VALIDATED_BY = "validated_by"
    RETRIED_WITH = "retried_with"
    OPTIMIZED_BY = "optimized_by"


class MemoryRelationship(BaseModel):
    relationship_id: str = Field(default_factory=lambda: str(uuid4()))
    source_id: str
    target_id: str
    rel_type: RelationshipType
    weight: float = 0.5
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
