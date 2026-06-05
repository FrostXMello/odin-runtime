"""Wake scheduler for idle daemon."""

from __future__ import annotations

from typing import Any


class WakeScheduler:
    def __init__(self) -> None:
        self._tasks: list[dict[str, Any]] = []

    def schedule(self, *, kind: str, delay_s: int) -> dict[str, Any]:
        task = {"kind": kind, "delay_s": delay_s, "status": "scheduled"}
        self._tasks.append(task)
        return task
