from __future__ import annotations
from typing import Any

class ThoughtStream:
    def __init__(self) -> None:
        self._items: list[dict] = []

    def push(self, text: str, *, kind: str = "thought") -> dict[str, Any]:
        item = {"text": text[:500], "kind": kind}
        self._items.append(item)
        return item

    def snapshot(self) -> list[dict]:
        return self._items[-50:]
