"""Temporal awareness across perception events."""

from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from typing import Any


class TemporalContext:
    def __init__(self, *, max_events: int = 100) -> None:
        self._events: deque[dict[str, Any]] = deque(maxlen=max_events)

    def record_event(self, kind: str, payload: Any) -> None:
        self._events.append(
            {
                "kind": kind,
                "payload": payload,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    def recent_summary(self, *, limit: int = 10) -> dict[str, Any]:
        recent = list(self._events)[-limit:]
        kinds = [e["kind"] for e in recent]
        return {"event_count": len(self._events), "recent_kinds": kinds, "events": recent}
