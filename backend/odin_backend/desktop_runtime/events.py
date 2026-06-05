"""Normalized desktop context event types."""

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class DesktopEventType(StrEnum):
    WINDOW_FOCUSED = "desktop.window.focused"
    TERMINAL_UPDATED = "terminal.session.updated"
    VSCODE_WORKSPACE = "vscode.workspace.changed"
    BROWSER_CONTEXT = "browser.context.updated"
    CLIPBOARD_CHANGED = "clipboard.changed"
    NOTIFICATION = "system.notification"
    ACTIVITY_STATE = "system.activity_state"


class DesktopContextEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: DesktopEventType
    collector: str  # electron_bridge | api_ingest | manual
    captured_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: dict[str, Any] = Field(default_factory=dict)
    explainable: dict[str, Any] = Field(default_factory=dict)
