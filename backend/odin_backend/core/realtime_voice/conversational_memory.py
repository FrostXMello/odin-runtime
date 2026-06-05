"""Persistent conversation sessions."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class ConversationalMemory:
    def __init__(self) -> None:
        self._turns: list[dict[str, Any]] = []

    def add_turn(self, *, role: str, content: str) -> dict[str, Any]:
        turn = {"role": role, "content": content, "at": datetime.now(timezone.utc).isoformat()}
        self._turns.append(turn)
        return turn

    def context(self, limit: int = 10) -> list[dict[str, Any]]:
        return self._turns[-limit:]
