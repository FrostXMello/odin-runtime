"""Project registry."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


class ProjectRegistry:
    def __init__(self) -> None:
        self._projects: dict[str, dict[str, Any]] = {}

    def register(self, *, name: str, path: str, metadata: dict | None = None) -> dict[str, Any]:
        pid = str(uuid4())
        entry = {
            "id": pid,
            "name": name,
            "path": path,
            "metadata": metadata or {},
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._projects[pid] = entry
        return entry

    def get(self, project_id: str) -> dict[str, Any] | None:
        return self._projects.get(project_id)

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._projects.values())
