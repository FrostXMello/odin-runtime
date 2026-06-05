"""Daemon persistent session tracking."""

from __future__ import annotations

from typing import Any


class DaemonSessions:
    def __init__(self) -> None:
        self._sessions: list[str] = []

    def register(self, session_id: str) -> None:
        if session_id not in self._sessions:
            self._sessions.append(session_id)

    def count(self) -> int:
        return len(self._sessions)
