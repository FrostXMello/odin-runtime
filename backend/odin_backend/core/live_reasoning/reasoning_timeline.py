from __future__ import annotations
from typing import Any


class ReasoningTimeline:
    def __init__(self) -> None:
        self._events: list[dict] = []

    def record(self, kind: str, payload: dict) -> None:
        self._events.append({"kind": kind, **payload})

    def playback(self, *, limit: int = 20) -> list[dict]:
        return self._events[-limit:]
