"""Project deadline tracking."""

from __future__ import annotations

from typing import Any


class ProjectDeadlines:
    def __init__(self) -> None:
        self._deadlines: list[dict[str, Any]] = []

    def add(self, *, project_id: str, due: str, label: str) -> dict[str, Any]:
        entry = {"project_id": project_id, "due": due, "label": label}
        self._deadlines.append(entry)
        return entry

    def upcoming(self) -> list[dict[str, Any]]:
        return self._deadlines[-10:]
