"""Detected operator workflow patterns."""

from __future__ import annotations

from typing import Any


class WorkflowPatterns:
    def __init__(self) -> None:
        self._patterns: dict[str, int] = {}

    def observe(self, pattern: str) -> dict[str, Any]:
        self._patterns[pattern] = self._patterns.get(pattern, 0) + 1
        return {"pattern": pattern, "count": self._patterns[pattern]}

    def top(self, n: int = 5) -> list[tuple[str, int]]:
        return sorted(self._patterns.items(), key=lambda x: -x[1])[:n]
