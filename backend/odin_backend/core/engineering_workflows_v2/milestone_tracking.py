from __future__ import annotations


class MilestoneTracker:
    def __init__(self) -> None:
        self._milestones: list[str] = []

    def add(self, name: str) -> None:
        self._milestones.append(name)

    def list(self) -> list[str]:
        return self._milestones[-16:]
