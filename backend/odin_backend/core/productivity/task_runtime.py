"""Persistent task tracking."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


class TaskRuntime:
    def __init__(self) -> None:
        self._tasks: dict[str, dict[str, Any]] = {}

    def create(self, *, title: str, project_id: str | None = None) -> dict[str, Any]:
        tid = str(uuid4())
        task = {
            "id": tid,
            "title": title,
            "project_id": project_id,
            "status": "open",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._tasks[tid] = task
        return task

    def complete(self, task_id: str) -> dict[str, Any] | None:
        task = self._tasks.get(task_id)
        if not task:
            return None
        task["status"] = "done"
        return task

    def list_open(self) -> list[dict[str, Any]]:
        return [t for t in self._tasks.values() if t["status"] != "done"]
