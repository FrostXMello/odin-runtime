"""Society debate sessions."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


class DebateSessions:
    def __init__(self) -> None:
        self._sessions: dict[str, dict[str, Any]] = {}

    def start(self, *, topic: str, participants: list[str]) -> dict[str, Any]:
        sid = str(uuid4())
        self._sessions[sid] = {
            "id": sid,
            "topic": topic,
            "participants": participants,
            "turns": [],
            "status": "active",
            "started_at": datetime.now(timezone.utc).isoformat(),
        }
        return self._sessions[sid]

    def add_turn(self, session_id: str, *, agent_id: str, content: str) -> dict[str, Any] | None:
        sess = self._sessions.get(session_id)
        if not sess:
            return None
        sess["turns"].append({"agent_id": agent_id, "content": content[:2000]})
        return sess

    def list_active(self) -> list[dict[str, Any]]:
        return [s for s in self._sessions.values() if s.get("status") == "active"]
