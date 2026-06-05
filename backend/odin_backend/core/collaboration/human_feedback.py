"""Operator feedback reinforcement."""

from __future__ import annotations

from collections import deque
from typing import Any


class HumanFeedbackStore:
    def __init__(self, *, max_entries: int = 40) -> None:
        self._entries: deque[dict[str, Any]] = deque(maxlen=max_entries)

    def record(self, *, kind: str, value: float, note: str = "") -> None:
        self._entries.append({"kind": kind, "value": max(-1.0, min(1.0, value)), "note": note[:500]})

    def recent(self) -> list[dict[str, Any]]:
        return list(self._entries)
