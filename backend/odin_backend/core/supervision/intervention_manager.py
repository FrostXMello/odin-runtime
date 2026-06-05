"""Operator intervention tracking."""

from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from typing import Any


class InterventionManager:
    def __init__(self) -> None:
        self._events: deque[dict[str, Any]] = deque(maxlen=50)

    def record(self, *, kind: str, detail: str = "") -> None:
        self._events.append(
            {"kind": kind, "detail": detail, "timestamp": datetime.now(timezone.utc).isoformat()}
        )

    def recent(self) -> list[dict[str, Any]]:
        return list(self._events)
