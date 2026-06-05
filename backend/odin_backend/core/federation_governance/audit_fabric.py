"""Federation audit log."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class AuditFabric:
    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []

    def record(self, *, action: str, node_id: str, detail: dict | None = None) -> dict[str, Any]:
        entry = {
            "action": action,
            "node_id": node_id,
            "detail": detail or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._entries.append(entry)
        return entry

    def recent(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._entries[-limit:]
