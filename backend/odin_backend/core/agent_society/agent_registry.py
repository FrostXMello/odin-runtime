"""In-memory society agent registry."""

from __future__ import annotations

from typing import Any


class SocietyAgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[str, dict[str, Any]] = {}

    def register(self, profile: dict[str, Any]) -> dict[str, Any]:
        self._agents[profile["agent_id"]] = profile
        return profile

    def get(self, agent_id: str) -> dict[str, Any] | None:
        return self._agents.get(agent_id)

    def list_ids(self) -> list[str]:
        return list(self._agents.keys())

    def count(self) -> int:
        return len(self._agents)
