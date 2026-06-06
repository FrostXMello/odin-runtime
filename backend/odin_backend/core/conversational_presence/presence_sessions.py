from __future__ import annotations
from typing import Any
from uuid import uuid4


class PresenceSessions:
    def __init__(self) -> None:
        self._sessions: dict[str, dict] = {}

    def open(self, *, thread_id: str = "") -> dict[str, Any]:
        sid = thread_id or str(uuid4())
        self._sessions[sid] = {"thread_id": sid, "turns": 0}
        return self._sessions[sid]

    def get(self, sid: str) -> dict | None:
        return self._sessions.get(sid)
