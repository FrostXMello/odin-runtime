"""Live workflow annotations."""

from __future__ import annotations

from collections import deque
from typing import Any


class ExecutionAnnotations:
    def __init__(self, *, max_items: int = 30) -> None:
        self._items: deque[dict[str, Any]] = deque(maxlen=max_items)

    def add(self, annotation: dict[str, Any]) -> None:
        self._items.append(annotation)

    def recent(self) -> list[dict[str, Any]]:
        return list(self._items)
