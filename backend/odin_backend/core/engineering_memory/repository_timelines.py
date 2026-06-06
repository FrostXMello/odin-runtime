"""Repository event timelines."""

from __future__ import annotations

from typing import Any


class RepositoryTimeline:
    def __init__(self) -> None:
        self._events: list[dict[str, Any]] = []

    def add(self, *, repo: str, event: str, detail: dict[str, Any]) -> dict[str, Any]:
        entry = {"repo": repo, "event": event, "detail": detail}
        self._events.append(entry)
        return entry

    def for_repo(self, repo: str) -> list[dict[str, Any]]:
        return [e for e in self._events if e["repo"] == repo]

    def count(self) -> int:
        return len(self._events)
