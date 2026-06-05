"""Habit tracking."""

from __future__ import annotations

from typing import Any


class HabitTracking:
    def __init__(self) -> None:
        self._counts: dict[str, int] = {}

    def record(self, habit: str) -> int:
        self._counts[habit] = self._counts.get(habit, 0) + 1
        return self._counts[habit]
