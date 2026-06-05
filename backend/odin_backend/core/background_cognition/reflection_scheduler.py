"""Schedule background reflection tasks."""

from __future__ import annotations

from typing import Any


class ReflectionScheduler:
    def __init__(self) -> None:
        self._tasks: list[dict[str, Any]] = []
        self._cancelled = False

    def schedule(self, *, kind: str) -> dict[str, Any]:
        task = {"kind": kind, "status": "scheduled", "cancellable": True}
        self._tasks.append(task)
        return task

    def cancel_all(self) -> int:
        self._cancelled = True
        for t in self._tasks:
            if t["status"] == "scheduled":
                t["status"] = "cancelled"
        return sum(1 for t in self._tasks if t["status"] == "cancelled")

    def pending(self) -> list[dict[str, Any]]:
        return [t for t in self._tasks if t["status"] == "scheduled"]
