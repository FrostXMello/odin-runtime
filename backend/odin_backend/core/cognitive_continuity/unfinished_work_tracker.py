from __future__ import annotations

from typing import Any


class UnfinishedWorkTracker:
    def __init__(self) -> None:
        self._items: list[dict[str, Any]] = []

    def add(self, *, title: str, project: str) -> dict[str, Any]:
        item = {"title": title, "project": project, "done": False}
        self._items.append(item)
        return item

    def list_all(self) -> list[dict[str, Any]]:
        return [i for i in self._items if not i.get("done")]
