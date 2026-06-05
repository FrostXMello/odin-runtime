"""Long-term context windows."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class LongTermContext:
    def __init__(self) -> None:
        self._windows: list[dict[str, Any]] = []

    def add(self, *, label: str, content: dict, horizon_days: int = 7) -> dict[str, Any]:
        entry = {
            "label": label,
            "content": content,
            "horizon_days": min(horizon_days, 90),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._windows.append(entry)
        return entry

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._windows)
