from __future__ import annotations
from collections import deque
from typing import Any


class TaskQueues:
    def __init__(self) -> None:
        self.active: deque[str] = deque(maxlen=32)
        self.background: deque[str] = deque(maxlen=64)
        self.deferred: deque[str] = deque(maxlen=128)
        self.overnight: deque[str] = deque(maxlen=64)

    def defer(self, task: str) -> None:
        self.deferred.append(task[:120])

    def restore(self) -> list[str]:
        restored = list(self.deferred)
        self.deferred.clear()
        return restored
