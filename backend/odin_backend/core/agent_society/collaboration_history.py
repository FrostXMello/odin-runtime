"""Collaboration history between agents."""

from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from typing import Any


class CollaborationHistory:
    def __init__(self, *, max_entries: int = 100) -> None:
        self._entries: deque[dict[str, Any]] = deque(maxlen=max_entries)

    def record(self, *, agents: list[str], kind: str, outcome: str = "ok") -> None:
        self._entries.append(
            {
                "agents": agents,
                "kind": kind,
                "outcome": outcome,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    def recent(self, *, limit: int = 30) -> list[dict[str, Any]]:
        return list(self._entries)[-limit:]
