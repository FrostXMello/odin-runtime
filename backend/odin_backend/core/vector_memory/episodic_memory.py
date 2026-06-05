"""Episodic memory replay."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class EpisodicMemory:
    def __init__(self) -> None:
        self._episodes: list[dict[str, Any]] = []

    def record(self, *, event: str, context: dict) -> dict[str, Any]:
        ep = {"event": event, "context": context, "at": datetime.now(timezone.utc).isoformat()}
        self._episodes.append(ep)
        return ep

    def replay(self, limit: int = 10) -> list[dict[str, Any]]:
        return self._episodes[-limit:]
