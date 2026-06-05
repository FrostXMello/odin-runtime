"""Request rate limiting."""

from __future__ import annotations

import time
from collections import deque


class RateLimiter:
    def __init__(self, *, max_per_minute: int = 20) -> None:
        self._max = max_per_minute
        self._hits: deque[float] = deque()

    def allow(self) -> bool:
        now = time.monotonic()
        self._hits = deque(t for t in self._hits if now - t < 60.0)
        if len(self._hits) >= self._max:
            return False
        self._hits.append(now)
        return True
