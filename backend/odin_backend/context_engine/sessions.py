"""Unified contextual session models."""

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class ApplicationContext(BaseModel):
    name: str
    window_title: str | None = None
    process_id: int | None = None


class BrowserTabContext(BaseModel):
    url: str
    title: str = ""
    tab_id: str | None = None


class TerminalContext(BaseModel):
    cwd: str | None = None
    shell: str | None = None
    recent_output_preview: str | None = None


class UnifiedContextSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    project: str = "PROJECT_ODIN"
    active_applications: list[ApplicationContext] = Field(default_factory=list)
    browser_tabs: list[BrowserTabContext] = Field(default_factory=list)
    terminals: list[TerminalContext] = Field(default_factory=list)
    active_workflow_ids: list[str] = Field(default_factory=list)
    conversation_session_id: str | None = None
    repository_path: str | None = None
    recent_interactions: list[str] = Field(default_factory=list)
    insight: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ContextSnapshot(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    label: str = "snapshot"
    session_data: dict[str, Any] = Field(default_factory=dict)
    summary: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
