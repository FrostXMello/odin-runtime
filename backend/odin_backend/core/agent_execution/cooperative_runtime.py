"""Cooperative async execution between agents."""

from __future__ import annotations

from typing import Any


class CooperativeRuntime:
    def __init__(self) -> None:
        self._collaborations: list[dict[str, Any]] = []

    def collaborate(self, *, agent_ids: list[str], task_id: str) -> dict[str, Any]:
        entry = {"agent_ids": agent_ids, "task_id": task_id, "status": "active"}
        self._collaborations.append(entry)
        return entry
