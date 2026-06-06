from __future__ import annotations


class ProjectTimeline:
    def __init__(self) -> None:
        self._events: list[dict] = []

    def add(self, kind: str, detail: str) -> None:
        self._events.append({"kind": kind, "detail": detail[:120]})

    def replay(self, limit: int = 24) -> list[dict]:
        return self._events[-limit:]
