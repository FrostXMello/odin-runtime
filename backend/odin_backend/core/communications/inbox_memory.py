"""Inbox memory for notifications."""

from __future__ import annotations

from typing import Any


class InboxMemory:
    def __init__(self) -> None:
        self._items: list[dict[str, Any]] = []

    def push(self, item: dict[str, Any]) -> None:
        self._items.append(item)
        if len(self._items) > 200:
            self._items = self._items[-200:]

    def unread(self) -> list[dict[str, Any]]:
        return [i for i in self._items if not i.get("read")][-20:]
