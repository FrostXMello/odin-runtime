from __future__ import annotations


class EpisodicThreads:
    def __init__(self) -> None:
        self._threads: list[dict] = []

    def add(self, topic: str) -> dict:
        t = {"topic": topic[:80]}
        self._threads.append(t)
        return t
