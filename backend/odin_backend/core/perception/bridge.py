"""Perception memory bridge."""

from typing import Any

from odin_backend.models.perception import PerceptionRecord


class PerceptionMemoryBridge:
    def __init__(self, store: Any, context_graph: Any) -> None:
        self._store = store
        self._graph = context_graph

    async def ingest(self, record: PerceptionRecord) -> str:
        mem_id = await self._store.record_perception(record)
        if record.mission_id:
            self._graph.upsert_node(
                f"mission:{record.mission_id}",
                "mission",
                f"Mission {record.mission_id[:8]}",
                {"last_perception": record.category.value},
            )
            self._graph.link(
                f"mission:{record.mission_id}",
                "system:odin",
                "perceived_by",
            )
        return mem_id
