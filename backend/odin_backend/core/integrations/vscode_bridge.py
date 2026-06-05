"""VSCode integration bridge (read-only)."""

from __future__ import annotations

from typing import Any


def parse_vscode_context(snapshot: dict[str, Any]) -> dict[str, Any]:
    return {
        "editor": "vscode",
        "active_file": snapshot.get("active_file"),
        "workspace_folders": snapshot.get("workspace_folders", []),
        "language": snapshot.get("language"),
    }
