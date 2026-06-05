"""Selective memory replication across nodes."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


class MemoryReplication:
    def __init__(self) -> None:
        self._replicas: list[dict[str, Any]] = []

    def replicate(self, *, source_node: str, target_node: str, memory_id: str) -> dict[str, Any]:
        entry = {
            "id": str(uuid4()),
            "source_node": source_node,
            "target_node": target_node,
            "memory_id": memory_id,
            "status": "replicated",
            "replicated_at": datetime.now(timezone.utc).isoformat(),
        }
        self._replicas.append(entry)
        return entry

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._replicas)
