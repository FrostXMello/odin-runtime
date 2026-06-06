from __future__ import annotations
from typing import Any


class ProposalQueue:
    def __init__(self) -> None:
        self._items: list[dict] = []

    def enqueue(self, item: dict) -> dict:
        self._items.append({**item, "status": "pending"})
        return self._items[-1]

    def pending(self) -> list[dict]:
        return [i for i in self._items if i.get("status") == "pending"]
