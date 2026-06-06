from __future__ import annotations
from typing import Any


class PatchTimeline:
    def __init__(self) -> None:
        self._events: list[dict] = []

    def add(self, event: dict) -> None:
        self._events.append(event)

    def history(self) -> list[dict]:
        return self._events[-32:]
