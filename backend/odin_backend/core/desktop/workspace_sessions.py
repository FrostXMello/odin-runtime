"""Workspace session timelines."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


class WorkspaceSessions:
    def __init__(self) -> None:
        self._sessions: list[dict[str, Any]] = []
        self._current_id = str(uuid4())

    def begin_segment(self, *, label: str) -> str:
        seg_id = str(uuid4())
        self._sessions.append(
            {
                "segment_id": seg_id,
                "label": label,
                "started_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        return seg_id

    def timeline(self, *, limit: int = 30) -> list[dict[str, Any]]:
        return self._sessions[-limit:]
