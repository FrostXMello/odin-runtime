"""Repository activity tracking."""

from __future__ import annotations

from typing import Any


class RepoActivity:
    def __init__(self) -> None:
        self._events: list[dict[str, Any]] = []

    def record(self, *, repo: str, event: str, detail: dict | None = None) -> dict[str, Any]:
        entry = {"repo": repo, "event": event, "detail": detail or {}}
        self._events.append(entry)
        return entry

    def heatmap(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._events[-limit:]
