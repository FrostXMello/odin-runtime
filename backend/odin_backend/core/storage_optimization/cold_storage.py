"""Cold storage tier."""

from __future__ import annotations

from typing import Any


class ColdStorage:
    def __init__(self) -> None:
        self._archived: list[dict[str, Any]] = []

    def store(self, entry: dict[str, Any]) -> None:
        self._archived.append(entry)

    def count(self) -> int:
        return len(self._archived)
