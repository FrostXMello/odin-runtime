from __future__ import annotations

class Timeline:
    def __init__(self) -> None:
        self._events: list[dict] = []

    def add(self, event: dict) -> None:
        self._events.append(event)

    def snapshot(self, limit: int = 30) -> list[dict]:
        return self._events[-limit:]
