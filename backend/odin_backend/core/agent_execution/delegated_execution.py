"""Delegated execution between agents."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


class DelegatedExecution:
    def __init__(self) -> None:
        self._leases: dict[str, dict[str, Any]] = {}

    def lease(self, *, task_id: str, agent_id: str, ttl_seconds: int = 300) -> dict[str, Any]:
        entry = {
            "lease_id": str(uuid4()),
            "task_id": task_id,
            "agent_id": agent_id,
            "leased_at": datetime.now(timezone.utc).isoformat(),
            "ttl_seconds": ttl_seconds,
        }
        self._leases[task_id] = entry
        return entry

    def owner(self, task_id: str) -> str | None:
        return self._leases.get(task_id, {}).get("agent_id")
