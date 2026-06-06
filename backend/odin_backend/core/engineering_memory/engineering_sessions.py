"""Persistent engineering sessions."""

from __future__ import annotations

from typing import Any
from uuid import uuid4


class EngineeringSessions:
    def __init__(self) -> None:
        self._sessions: list[dict[str, Any]] = []

    def start(self, *, repo: str, focus: str) -> dict[str, Any]:
        session = {"id": str(uuid4()), "repo": repo, "focus": focus, "active": True}
        self._sessions.append(session)
        return session

    def abandoned(self, *, hours: float = 24) -> list[dict[str, Any]]:
        return [s for s in self._sessions if s.get("active") and not s.get("completed")]

    def count(self) -> int:
        return len(self._sessions)
