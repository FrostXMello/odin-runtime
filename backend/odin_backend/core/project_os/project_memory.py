"""Per-project memory store."""

from __future__ import annotations

from typing import Any


class ProjectMemory:
    def __init__(self) -> None:
        self._entries: dict[str, list[dict[str, Any]]] = {}

    def append(self, project_id: str, *, text: str, kind: str = "note") -> dict[str, Any]:
        entry = {"text": text, "kind": kind}
        self._entries.setdefault(project_id, []).append(entry)
        return entry

    def timeline(self, project_id: str, limit: int = 50) -> list[dict[str, Any]]:
        return self._entries.get(project_id, [])[-limit:]
