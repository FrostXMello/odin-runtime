"""Visual memory for screenshot grounding."""

from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from typing import Any


class VisualMemory:
    def __init__(self, *, max_entries: int = 32) -> None:
        self._entries: deque[dict[str, Any]] = deque(maxlen=max_entries)

    def store(self, path: str, analysis: dict[str, Any]) -> None:
        self._entries.append(
            {
                "path": path,
                "analysis": analysis,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    def recent(self, *, limit: int = 5) -> list[dict[str, Any]]:
        return list(self._entries)[-limit:]
