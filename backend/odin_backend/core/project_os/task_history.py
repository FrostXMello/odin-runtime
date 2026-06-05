"""Project task history."""

from __future__ import annotations

from typing import Any


class TaskHistory:
    def __init__(self) -> None:
        self._history: dict[str, list[dict[str, Any]]] = {}

    def record(self, project_id: str, *, task: str, status: str) -> dict[str, Any]:
        entry = {"task": task, "status": status}
        self._history.setdefault(project_id, []).append(entry)
        return entry

    def list_for(self, project_id: str) -> list[dict[str, Any]]:
        return self._history.get(project_id, [])
