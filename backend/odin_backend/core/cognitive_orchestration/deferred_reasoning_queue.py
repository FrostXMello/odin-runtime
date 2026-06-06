from __future__ import annotations


class DeferredReasoningQueue:
    def __init__(self) -> None:
        self._queue: list[str] = []

    def defer(self, thought: str) -> None:
        self._queue.append(thought[:120])

    def drain(self, limit: int = 4) -> list[str]:
        out = self._queue[:limit]
        self._queue = self._queue[limit:]
        return out
