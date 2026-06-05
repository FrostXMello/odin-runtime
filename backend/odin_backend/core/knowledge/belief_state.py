"""Belief revision state."""

from __future__ import annotations

from typing import Any


class BeliefState:
    def __init__(self) -> None:
        self._beliefs: dict[str, dict[str, Any]] = {}

    def update(self, entity: str, *, fact: str, confidence: float, source: str) -> dict[str, Any]:
        key = f"{entity}:{fact[:80]}"
        prev = self._beliefs.get(key, {})
        entry = {
            "entity": entity,
            "fact": fact,
            "confidence": confidence,
            "source": source,
            "previous_confidence": prev.get("confidence"),
        }
        self._beliefs[key] = entry
        return entry

    def snapshot(self) -> list[dict[str, Any]]:
        return list(self._beliefs.values())
