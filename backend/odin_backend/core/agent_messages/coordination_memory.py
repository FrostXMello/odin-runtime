"""Persisted coordination memory."""

from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from typing import Any


class CoordinationMemory:
    def __init__(self, *, max_entries: int = 200) -> None:
        self._entries: deque[dict[str, Any]] = deque(maxlen=max_entries)

    def record(self, entry: dict[str, Any]) -> None:
        entry["timestamp"] = datetime.now(timezone.utc).isoformat()
        self._entries.append(entry)

    def recent(self, *, limit: int = 50) -> list[dict[str, Any]]:
        return list(self._entries)[-limit:]
