"""Action review queue."""

from __future__ import annotations

from collections import deque
from typing import Any


class ActionReviewQueue:
    def __init__(self) -> None:
        self._pending: deque[dict[str, Any]] = deque()

    def enqueue(self, action: dict[str, Any]) -> dict[str, Any]:
        self._pending.append(action)
        return action

    def pending(self) -> list[dict[str, Any]]:
        return list(self._pending)

    def pop(self, action_id: str) -> dict[str, Any] | None:
        items = list(self._pending)
        self._pending.clear()
        found = None
        for item in items:
            if item.get("id") == action_id:
                found = item
            else:
                self._pending.append(item)
        return found
