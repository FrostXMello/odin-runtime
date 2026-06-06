from __future__ import annotations

class DeferredQueue:
    def __init__(self) -> None:
        self._items: list[str] = []

    def defer(self, thought: str) -> dict:
        self._items.append(thought[:500])
        return {"queued": len(self._items)}

    def drain(self, limit: int = 5) -> list[str]:
        out = self._items[:limit]
        self._items = self._items[limit:]
        return out
