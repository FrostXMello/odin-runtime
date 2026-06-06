"""Episodic memory indexing."""

from __future__ import annotations

from typing import Any


class EpisodicIndex:
    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []

    def add(self, *, event: str, context: dict, age_hours: float = 0) -> dict[str, Any]:
        entry = {"event": event, "context": context, "age_hours": age_hours}
        self._entries.append(entry)
        return entry

    def search(self, *, query: str, limit: int = 5) -> list[dict[str, Any]]:
        q = query.lower()
        hits = [e for e in self._entries if q in e["event"].lower() or q in str(e["context"]).lower()]
        return hits[-limit:]

    def count(self) -> int:
        return len(self._entries)
