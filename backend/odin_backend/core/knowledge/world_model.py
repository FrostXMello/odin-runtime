"""Evolving world state model."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class WorldModel:
    def __init__(self) -> None:
        self._entities: dict[str, dict[str, Any]] = {}
        self._updated_at: datetime | None = None

    def apply_fact(self, *, entity: str, fact: str, confidence: float) -> None:
        state = self._entities.setdefault(entity, {"facts": [], "confidence": 0.0})
        state["facts"].append({"fact": fact, "confidence": confidence})
        state["facts"] = state["facts"][-10:]
        state["confidence"] = max(state.get("confidence", 0.0), confidence)
        self._updated_at = datetime.now(timezone.utc)

    def snapshot(self) -> dict[str, Any]:
        return {
            "entities": dict(self._entities),
            "entity_count": len(self._entities),
            "updated_at": self._updated_at.isoformat() if self._updated_at else None,
        }
