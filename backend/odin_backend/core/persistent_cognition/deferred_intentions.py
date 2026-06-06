from __future__ import annotations

class DeferredIntentions:
    def __init__(self) -> None:
        self._items: list[dict] = []

    def defer(self, intention: str, priority: float = 0.5) -> dict:
        item = {"intention": intention[:500], "priority": priority}
        self._items.append(item)
        return item

    def pending(self) -> list[dict]:
        return list(self._items)
