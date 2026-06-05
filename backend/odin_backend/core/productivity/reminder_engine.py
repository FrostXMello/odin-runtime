"""Contextual reminders."""

from __future__ import annotations

from typing import Any


class ReminderEngine:
    def __init__(self) -> None:
        self._reminders: list[dict[str, Any]] = []

    def add(self, *, text: str, context: str = "") -> dict[str, Any]:
        entry = {"text": text, "context": context}
        self._reminders.append(entry)
        return entry

    def due(self) -> list[dict[str, Any]]:
        return self._reminders[-10:]
