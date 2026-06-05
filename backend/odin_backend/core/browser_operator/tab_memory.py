"""Tab memory for browser workflows."""

from __future__ import annotations

from collections import deque
from typing import Any


class TabMemory:
    def __init__(self, *, max_tabs: int = 30) -> None:
        self._tabs: deque[dict[str, Any]] = deque(maxlen=max_tabs)

    def record(self, tab: dict[str, Any]) -> None:
        self._tabs.append(tab)

    def recent(self) -> list[dict[str, Any]]:
        return list(self._tabs)
