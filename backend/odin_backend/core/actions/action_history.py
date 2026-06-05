"""Persistent action history."""

from __future__ import annotations

from collections import deque
from typing import Any


class ActionHistory:
    def __init__(self, *, max_entries: int = 200) -> None:
        self._entries: deque[dict[str, Any]] = deque(maxlen=max_entries)

    def record(self, entry: dict[str, Any]) -> None:
        self._entries.append(entry)

    def recent(self, *, limit: int = 50) -> list[dict[str, Any]]:
        return list(self._entries)[-limit:]

    def find(self, action_id: str) -> dict[str, Any] | None:
        for e in reversed(self._entries):
            if e.get("id") == action_id:
                return e
        return None
