from __future__ import annotations

class UnfinishedWork:
    def __init__(self) -> None:
        self._items: list[dict] = []

    def track(self, *, title: str, project: str) -> dict:
        item = {"title": title[:200], "project": project[:80]}
        self._items.append(item)
        return item

    def abandoned(self, *, threshold_h: float = 24) -> list[dict]:
        return self._items
