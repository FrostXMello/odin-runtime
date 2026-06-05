"""Mission memory index — link episodic/semantic memory to missions."""

from typing import Any

from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class MissionMemoryIndex:
    """Indexes mission-linked memories for replay and audit."""

    def __init__(self, memory_coordinator: Any) -> None:
        self._memory = memory_coordinator
        self._index: dict[str, list[str]] = {}

    async def link_mission_start(self, mission_id: str, objective: str) -> str:
        mem_id = await self._memory.save_memory(
            f"Mission started: {objective}",
            category="mission",
            metadata={"mission_id": mission_id, "kind": "mission_start"},
        )
        self._register(mission_id, mem_id)
        return mem_id

    async def link_task_completion(self, mission_id: str, task_id: str, goal: str) -> str:
        mem_id = await self._memory.save_memory(
            f"Mission task complete [{task_id}]: {goal[:200]}",
            category="mission",
            metadata={"mission_id": mission_id, "task_id": task_id, "kind": "task_complete"},
        )
        self._register(mission_id, mem_id)
        return mem_id

    async def link_mission_complete(self, mission_id: str, objective: str) -> str:
        mem_id = await self._memory.save_memory(
            f"Mission completed: {objective}",
            category="mission",
            metadata={"mission_id": mission_id, "kind": "mission_complete"},
        )
        self._register(mission_id, mem_id)
        return mem_id

    async def link_checkpoint(self, mission_id: str, checkpoint_id: str, label: str) -> str:
        mem_id = await self._memory.save_memory(
            f"Mission checkpoint [{label}]",
            category="mission",
            metadata={
                "mission_id": mission_id,
                "checkpoint_id": checkpoint_id,
                "kind": "checkpoint",
            },
        )
        self._register(mission_id, mem_id)
        return mem_id

    def _register(self, mission_id: str, memory_id: str) -> None:
        refs = self._index.setdefault(mission_id, [])
        if memory_id not in refs:
            refs.append(memory_id)

    def refs_for_mission(self, mission_id: str) -> list[str]:
        return list(self._index.get(mission_id, []))

    async def replay(self, mission_id: str, limit: int = 20) -> list[dict[str, Any]]:
        refs = self.refs_for_mission(mission_id)
        if not refs:
            results = await self._memory.search_memory(f"mission_id:{mission_id}", limit=limit)
            return results
        out: list[dict[str, Any]] = []
        for mid in refs[-limit:]:
            out.append({"memory_id": mid, "mission_id": mission_id})
        return out
