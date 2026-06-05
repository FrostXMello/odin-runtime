"""Daemon startup and recovery."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class StartupManager:
    def __init__(self) -> None:
        self._started_at: str | None = None
        self._recoveries: int = 0

    def mark_started(self) -> dict[str, Any]:
        self._started_at = datetime.now(timezone.utc).isoformat()
        return {"started_at": self._started_at}

    def mark_recovery(self) -> dict[str, Any]:
        self._recoveries += 1
        return {"recoveries": self._recoveries}
