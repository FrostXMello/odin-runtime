"""Active topic tracking."""

from __future__ import annotations

from typing import Any


class TopicTracker:
    def __init__(self) -> None:
        self._topics: dict[str, dict[str, Any]] = {}

    def track(self, topic: str, *, metadata: dict | None = None) -> dict[str, Any]:
        entry = self._topics.setdefault(topic, {"topic": topic, "updates": 0, "metadata": {}})
        entry["updates"] += 1
        if metadata:
            entry["metadata"].update(metadata)
        return entry

    def list_topics(self) -> list[dict[str, Any]]:
        return list(self._topics.values())
