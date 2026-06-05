"""Timeline reconstruction."""

from __future__ import annotations

from typing import Any


def build_timeline(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(events, key=lambda e: e.get("at", ""))[-100:]
