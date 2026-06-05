"""Federation trust scoring."""

from __future__ import annotations

from typing import Any


class TrustEngine:
    def __init__(self) -> None:
        self._scores: dict[str, float] = {}

    def score(self, node_id: str, *, delta: float = 0.0) -> float:
        current = self._scores.get(node_id, 0.5)
        updated = min(1.0, max(0.0, current + delta))
        self._scores[node_id] = updated
        return updated

    def get(self, node_id: str) -> float:
        return self._scores.get(node_id, 0.5)

    def snapshot(self) -> dict[str, float]:
        return dict(self._scores)
