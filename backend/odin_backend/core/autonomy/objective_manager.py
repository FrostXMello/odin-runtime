"""Objective manager — bridges graph to autonomous missions."""

from __future__ import annotations

from typing import Any

from odin_backend.core.autonomy.objective_graph import (
    PersistentObjective,
    PersistentObjectiveGraph,
)


class ObjectiveManager:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._graph = PersistentObjectiveGraph(app.settings)

    @property
    def graph(self) -> PersistentObjectiveGraph:
        return self._graph

    async def connect(self) -> None:
        await self._graph.connect()

    async def disconnect(self) -> None:
        await self._graph.disconnect()

    async def create(self, *, title: str, description: str = "", priority: float = 0.5) -> PersistentObjective:
        obj = PersistentObjective(title=title, description=description, priority=priority)
        return await self._graph.upsert(obj)

    async def list_all(self, *, status: str | None = None) -> list[PersistentObjective]:
        return await self._graph.list_objectives(status=status)

    async def mission_objective_for(self, obj: PersistentObjective) -> str:
        return f"[Autonomous] {obj.title}: {obj.description}"[:500]
