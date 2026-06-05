"""Persistent daemon heartbeat."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class HeartbeatPersistence:
    def __init__(self) -> None:
        self._beats: list[dict[str, Any]] = []
        self._last: str | None = None

    def beat(self, *, component: str = "daemon", uptime_s: float = 0) -> dict[str, Any]:
        entry = {
            "component": component,
            "at": datetime.now(timezone.utc).isoformat(),
            "uptime_s": uptime_s,
        }
        self._last = entry["at"]
        self._beats.append(entry)
        if len(self._beats) > 500:
            self._beats = self._beats[-500:]
        return entry

    def snapshot(self) -> dict[str, Any]:
        return {"last": self._last, "count": len(self._beats)}
