"""Objective-linked task scheduling."""

from __future__ import annotations

from typing import Any


class ObjectiveScheduler:
    def __init__(self) -> None:
        self._queue: list[dict[str, Any]] = []

    def enqueue(self, *, task_id: str, priority: float = 0.5) -> dict[str, Any]:
        entry = {"task_id": task_id, "priority": priority}
        self._queue.append(entry)
        self._queue.sort(key=lambda x: -x["priority"])
        return entry

    def next_task(self) -> dict[str, Any] | None:
        return self._queue.pop(0) if self._queue else None
