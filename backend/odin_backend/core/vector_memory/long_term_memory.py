"""Long-term memory with importance decay."""

from __future__ import annotations

from typing import Any


class LongTermMemory:
    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []

    def store(self, *, content: str, importance: float) -> dict[str, Any]:
        entry = {"content": content, "importance": importance, "access_count": 0}
        self._entries.append(entry)
        return entry

    def retrieve(self, *, min_importance: float = 0.3, limit: int = 10) -> list[dict[str, Any]]:
        ranked = sorted(self._entries, key=lambda e: e["importance"], reverse=True)
        return [e for e in ranked if e["importance"] >= min_importance][:limit]
