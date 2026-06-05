"""Structured perception models."""

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class PerceptionCategory(StrEnum):
    PERCEPTION_EVENT = "perception.event"
    EXECUTION_RESULT = "execution.result"
    ENVIRONMENT_CHANGE = "environment.change"
    MISSION_FEEDBACK = "mission.feedback"
    FAILURE_DETECTED = "failure.detected"
    GOAL_DRIFT = "goal.drift"
    RESOURCE_WARNING = "resource.warning"


class PerceptionRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    category: PerceptionCategory
    source: str = "observer"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    mission_id: str | None = None
    task_id: str | None = None
    tool: str | None = None
    summary: str = ""
    payload: dict[str, Any] = Field(default_factory=dict)
    confidence_impact: float = 0.0
