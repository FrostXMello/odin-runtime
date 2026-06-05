"""Execution memory replay for agent tasks."""

from __future__ import annotations

from typing import Any


class ExecutionMemory:
    def __init__(self) -> None:
        self._records: list[dict[str, Any]] = []

    def record(self, *, task_id: str, outcome: str) -> dict[str, Any]:
        entry = {"task_id": task_id, "outcome": outcome}
        self._records.append(entry)
        return entry

    def for_task(self, task_id: str) -> list[dict[str, Any]]:
        return [r for r in self._records if r["task_id"] == task_id]
