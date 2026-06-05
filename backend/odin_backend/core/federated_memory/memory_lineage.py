"""Memory source lineage tracking."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class MemoryLineage:
    def __init__(self) -> None:
        self._lineage: dict[str, list[str]] = {}

    def record(self, memory_id: str, *, source: str) -> dict[str, Any]:
        self._lineage.setdefault(memory_id, []).append(source)
        return {
            "memory_id": memory_id,
            "sources": list(self._lineage[memory_id]),
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        }

    def get(self, memory_id: str) -> list[str]:
        return list(self._lineage.get(memory_id, []))
