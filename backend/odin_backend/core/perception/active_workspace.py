"""Active workspace session tracking."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


class ActiveWorkspace:
    def __init__(self) -> None:
        self._session_id = str(uuid4())
        self._project: str | None = None
        self._apps: list[str] = []
        self._started_at = datetime.now(timezone.utc)

    def update_from_snapshot(self, snapshot: dict[str, Any]) -> None:
        if snapshot.get("project"):
            self._project = str(snapshot["project"])
        win = snapshot.get("active_window") or {}
        app = win.get("app") or win.get("title")
        if app and app not in self._apps:
            self._apps.append(str(app))
            self._apps = self._apps[-15:]

    def snapshot(self) -> dict[str, Any]:
        return {
            "session_id": self._session_id,
            "project": self._project,
            "apps": self._apps,
            "started_at": self._started_at.isoformat(),
        }
