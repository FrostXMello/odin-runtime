"""Note relationship linking."""

from __future__ import annotations

from typing import Any


class NoteLinking:
    def __init__(self) -> None:
        self._edges: list[tuple[str, str]] = []

    def link(self, a: str, b: str) -> None:
        self._edges.append((a, b))

    def neighbors(self, node: str) -> list[str]:
        return [b for x, b in self._edges if x == node] + [a for a, y in self._edges if y == node]
