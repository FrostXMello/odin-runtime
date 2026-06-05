"""Local notification event buffer."""

from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from typing import Any


class NotificationListener:
    def __init__(self, *, max_items: int = 50) -> None:
        self._items: deque[dict[str, Any]] = deque(maxlen=max_items)

    def push(self, *, title: str, body: str = "", app: str = "") -> None:
        self._items.append(
            {
                "title": title[:200],
                "body": body[:500],
                "app": app[:64],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    def recent(self) -> list[dict[str, Any]]:
        return list(self._items)
