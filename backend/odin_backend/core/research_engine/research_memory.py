"""Longitudinal research memory."""

from __future__ import annotations

from collections import deque
from typing import Any


class ResearchMemory:
    def __init__(self, *, max_sessions: int = 50) -> None:
        self._sessions: deque[dict[str, Any]] = deque(maxlen=max_sessions)

    def record(self, session: dict[str, Any]) -> None:
        self._sessions.append(session)

    def recent(self) -> list[dict[str, Any]]:
        return list(self._sessions)
