"""Detect runaway autonomy loops."""

from __future__ import annotations

import time
from collections import deque


class LoopDetector:
    def __init__(self, *, window_seconds: float = 300.0, max_events: int = 20) -> None:
        self._events: deque[float] = deque(maxlen=max_events)
        self._window = window_seconds

    def record(self) -> int:
        now = time.time()
        self._events.append(now)
        cutoff = now - self._window
        while self._events and self._events[0] < cutoff:
            self._events.popleft()
        return len(self._events)

    def is_runaway(self, *, threshold: int = 15) -> bool:
        return len(self._events) >= threshold
