"""Bounded behavioral traits per agent."""

from __future__ import annotations

from typing import Any

from odin_backend.core.agent_society.personality_bounds import bounded_update


class BehavioralTraits:
    def __init__(self) -> None:
        self._traits: dict[str, dict[str, float]] = {}

    def get(self, agent_id: str) -> dict[str, float]:
        return dict(self._traits.get(agent_id, {"curiosity": 0.5, "caution": 0.5, "collaboration": 0.5}))

    def adjust(self, agent_id: str, *, trait: str, delta: float) -> dict[str, float]:
        current = self.get(agent_id)
        current[trait] = bounded_update(current.get(trait, 0.5), delta)
        self._traits[agent_id] = current
        return current
