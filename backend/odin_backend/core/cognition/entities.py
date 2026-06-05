"""Cognitive memory graph entities."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class MemoryEntityKind(StrEnum):
    MISSION = "mission"
    TASK = "task"
    EXECUTION = "execution"
    CAPABILITY = "capability"
    TOOL = "tool"
    STRATEGY = "strategy"
    PATTERN = "pattern"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"


class MemoryEntity(BaseModel):
    entity_id: str = Field(default_factory=lambda: str(uuid4()))
    kind: MemoryEntityKind
    label: str
    confidence: float = 0.5
    reinforcement: float = 0.0
    mission_id: str | None = None
    task_id: str | None = None
    execution_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def touch(self, *, delta_reinforcement: float = 0.0, success: bool | None = None) -> None:
        self.updated_at = datetime.now(timezone.utc)
        if delta_reinforcement:
            self.reinforcement += delta_reinforcement
        if success is True:
            self.confidence = min(0.99, self.confidence + 0.05)
        elif success is False:
            self.confidence = max(0.05, self.confidence - 0.08)
