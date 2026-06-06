from __future__ import annotations

from typing import Any


class MilestoneTracker:
    def __init__(self) -> None:
        self._milestones: list[dict[str, Any]] = []

    def add(self, *, name: str) -> dict[str, Any]:
        m = {"name": name, "complete": False}
        self._milestones.append(m)
        return m

    def count(self) -> int:
        return len(self._milestones)
