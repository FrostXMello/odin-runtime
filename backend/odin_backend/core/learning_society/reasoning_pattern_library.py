"""Distilled reasoning patterns."""

from __future__ import annotations

from typing import Any


class ReasoningPatternLibrary:
    def __init__(self) -> None:
        self._patterns: list[dict[str, Any]] = []

    def add(self, *, name: str, steps: list[str], source_agent: str) -> dict[str, Any]:
        entry = {"name": name, "steps": steps, "source_agent": source_agent}
        self._patterns.append(entry)
        if len(self._patterns) > 100:
            self._patterns = self._patterns[-100:]
        return entry

    def list_patterns(self) -> list[dict[str, Any]]:
        return list(self._patterns)[-20:]
