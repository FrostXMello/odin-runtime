"""Mission generation throttles."""

from __future__ import annotations

import time


class MissionThrottle:
    def __init__(self, *, max_per_hour: int = 5) -> None:
        self._max = max_per_hour
        self._timestamps: list[float] = []

    def record(self) -> None:
        self._timestamps.append(time.time())
        self._prune()

    def allow(self) -> bool:
        self._prune()
        return len(self._timestamps) < self._max

    def _prune(self) -> None:
        cutoff = time.time() - 3600
        self._timestamps = [t for t in self._timestamps if t >= cutoff]
