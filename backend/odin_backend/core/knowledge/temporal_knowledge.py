"""Temporal fact tracking."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class TemporalKnowledge:
    def __init__(self) -> None:
        self._snapshots: list[dict[str, Any]] = []

    def record(self, *, entity: str, fact: str, confidence: float) -> None:
        self._snapshots.append(
            {
                "entity": entity,
                "fact": fact,
                "confidence": confidence,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        if len(self._snapshots) > 500:
            self._snapshots = self._snapshots[-500:]

    def history(self, entity: str) -> list[dict[str, Any]]:
        return [s for s in self._snapshots if s.get("entity") == entity]
