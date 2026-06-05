"""Distributed delegation across nodes."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


class DistributedDelegation:
    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []

    def create(self, *, from_node: str, to_node: str, task: str, mission_id: str | None = None) -> dict[str, Any]:
        entry = {
            "id": str(uuid4()),
            "from_node": from_node,
            "to_node": to_node,
            "task": task,
            "mission_id": mission_id,
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._entries.append(entry)
        return entry

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._entries)

    def list_for_mission(self, mission_id: str) -> list[dict[str, Any]]:
        return [e for e in self._entries if e.get("mission_id") == mission_id]
