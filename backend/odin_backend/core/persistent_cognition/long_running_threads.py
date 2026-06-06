from __future__ import annotations

class LongRunningThreads:
    def __init__(self) -> None:
        self._threads: dict[str, list[dict]] = {}

    def append(self, thread_id: str, item: dict) -> str:
        self._threads.setdefault(thread_id, []).append(item)
        return thread_id

    def get(self, thread_id: str) -> list[dict]:
        return self._threads.get(thread_id, [])
