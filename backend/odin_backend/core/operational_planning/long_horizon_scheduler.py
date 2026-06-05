"""Long-horizon scheduling."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Any
from uuid import uuid4


class LongHorizonScheduler:
    def __init__(self) -> None:
        self._items: list[dict[str, Any]] = []

    def schedule(self, *, title: str, horizon_days: int = 14) -> dict[str, Any]:
        item = {
            "id": str(uuid4()),
            "title": title,
            "horizon_days": min(horizon_days, 90),
            "scheduled_for": (datetime.now(timezone.utc) + timedelta(days=horizon_days)).isoformat(),
            "status": "scheduled",
        }
        self._items.append(item)
        return item

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._items)
