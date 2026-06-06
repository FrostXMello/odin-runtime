from __future__ import annotations

from typing import Any


class DeferredThoughts:
    def __init__(self) -> None:
        self._items: list[str] = []

    def add(self, thought: str) -> dict[str, Any]:
        self._items.append(thought[:500])
        return {"thought": thought[:80], "queue_size": len(self._items)}

    def list_all(self) -> list[str]:
        return list(self._items)
