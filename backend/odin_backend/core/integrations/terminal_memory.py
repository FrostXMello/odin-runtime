"""Terminal session memory."""

from __future__ import annotations

from typing import Any


class TerminalMemory:
    def __init__(self) -> None:
        self._sessions: dict[str, list[str]] = {}

    def append(self, session_id: str, line: str) -> None:
        self._sessions.setdefault(session_id, []).append(line)
        if len(self._sessions[session_id]) > 500:
            self._sessions[session_id] = self._sessions[session_id][-500:]

    def history(self, session_id: str, limit: int = 50) -> list[str]:
        return self._sessions.get(session_id, [])[-limit:]
