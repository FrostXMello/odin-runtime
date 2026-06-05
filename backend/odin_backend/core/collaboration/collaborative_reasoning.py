"""Collaborative planning sessions."""

from __future__ import annotations

from typing import Any
from uuid import uuid4


class CollaborativeReasoning:
    def __init__(self) -> None:
        self._sessions: dict[str, dict[str, Any]] = {}

    def start(self, *, topic: str) -> dict[str, Any]:
        sid = str(uuid4())
        self._sessions[sid] = {"id": sid, "topic": topic[:300], "turns": []}
        return self._sessions[sid]

    def add_turn(self, session_id: str, *, role: str, content: str) -> dict[str, Any] | None:
        sess = self._sessions.get(session_id)
        if not sess:
            return None
        sess["turns"].append({"role": role, "content": content[:2000]})
        return sess

    def list_sessions(self) -> list[dict[str, Any]]:
        return list(self._sessions.values())[-10:]
