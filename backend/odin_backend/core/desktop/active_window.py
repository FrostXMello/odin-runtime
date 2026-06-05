"""Active window tracking."""

from __future__ import annotations

from typing import Any


def parse_active_window(snapshot: dict[str, Any]) -> dict[str, Any]:
    win = snapshot.get("active_window") or {}
    return {
        "title": win.get("title", ""),
        "app": win.get("app") or win.get("process", "unknown"),
        "pid": win.get("pid"),
    }
