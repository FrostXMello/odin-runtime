"""Cursor IDE bridge (read-only)."""

from __future__ import annotations

from typing import Any


def parse_cursor_context(snapshot: dict[str, Any]) -> dict[str, Any]:
    return {
        "editor": "cursor",
        "active_file": snapshot.get("active_file"),
        "workspace_folders": snapshot.get("workspace_folders", []),
        "agent_mode": snapshot.get("agent_mode", False),
    }
