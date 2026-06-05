"""Delegation planning between agents."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


class DelegationPlanner:
    def __init__(self) -> None:
        self._delegations: dict[str, dict[str, Any]] = {}

    def create(self, *, from_agent: str, to_agent: str, task: str, mission_id: str | None = None) -> dict[str, Any]:
        did = str(uuid4())
        entry = {
            "id": did,
            "from_agent": from_agent,
            "to_agent": to_agent,
            "task": task[:500],
            "mission_id": mission_id,
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._delegations[did] = entry
        return entry

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._delegations.values())[-30:]
