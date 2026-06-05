"""Active app UI understanding."""

from __future__ import annotations

from typing import Any


def understand(snapshot: dict) -> dict[str, Any]:
    return {
        "window_title": snapshot.get("title", ""),
        "app": snapshot.get("app", "unknown"),
        "elements_detected": len(snapshot.get("elements", [])),
    }
