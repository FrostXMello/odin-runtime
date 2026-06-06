from __future__ import annotations
from typing import Any

class ImprovementQueue:
    def __init__(self) -> None:
        self._items: list[dict] = []

    def enqueue(self, item: dict) -> dict[str, Any]:
        item = {**item, "status": "proposed", "approval_required": True}
        self._items.append(item)
        return item

    def snapshot(self) -> list[dict]:
        return list(self._items)
