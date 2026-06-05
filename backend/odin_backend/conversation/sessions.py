"""Conversation session models."""

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConversationMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class ActiveObjective(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    description: str
    workflow_id: str | None = None
    status: str = "active"  # active | paused | completed | cancelled
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ConversationSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = "New conversation"
    messages: list[ConversationMessage] = Field(default_factory=list)
    active_objectives: list[ActiveObjective] = Field(default_factory=list)
    linked_workflow_ids: list[str] = Field(default_factory=list)
    compressed_summary: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
