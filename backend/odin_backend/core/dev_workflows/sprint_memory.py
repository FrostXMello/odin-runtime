from __future__ import annotations

from typing import Any


class SprintMemory:
    def __init__(self) -> None:
        self._sprints: list[dict[str, Any]] = []

    def record(self, *, name: str, tasks: list[str]) -> dict[str, Any]:
        entry = {"name": name, "tasks": tasks}
        self._sprints.append(entry)
        return entry

    def count(self) -> int:
        return len(self._sprints)
