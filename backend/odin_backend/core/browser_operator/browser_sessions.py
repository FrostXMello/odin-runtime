"""Browser session tracking."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


class BrowserSessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, dict[str, Any]] = {}
        self._active: str | None = None

    def start(self) -> dict[str, Any]:
        sid = str(uuid4())
        sess = {"id": sid, "started_at": datetime.now(timezone.utc).isoformat(), "tabs": []}
        self._sessions[sid] = sess
        self._active = sid
        return sess

    def active(self) -> dict[str, Any] | None:
        if self._active:
            return self._sessions.get(self._active)
        return None

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._sessions.values())
