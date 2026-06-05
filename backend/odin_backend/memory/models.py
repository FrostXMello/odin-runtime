"""Unified memory item schema."""

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class MemoryItemType(StrEnum):
    FACT = "fact"
    EVENT = "event"
    PREFERENCE = "preference"
    DECISION = "decision"
    OUTCOME = "outcome"


class MemoryItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: MemoryItemType = MemoryItemType.FACT
    content: dict[str, Any] = Field(default_factory=dict)
    embedding: list[float] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source: str = "system"

    @classmethod
    def from_legacy(
        cls,
        *,
        memory_id: str,
        text: str,
        category: str | None = None,
        metadata: dict | None = None,
    ) -> "MemoryItem":
        item_type = MemoryItemType.FACT
        if category in ("preference", "event", "decision", "outcome"):
            item_type = MemoryItemType(category)
        return cls(
            id=memory_id,
            type=item_type,
            content={"text": text, **(metadata or {})},
            source=metadata.get("source", "mimir") if metadata else "mimir",
        )
