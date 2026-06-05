"""Mission state store — durable persistence facade."""

from typing import Any

from odin_backend.memory.structured.mission_store import MissionStructuredStore
from odin_backend.models.mission import Mission, MissionLifecycle


class MissionStateStore:
    def __init__(self, structured_store: Any) -> None:
        self._db = MissionStructuredStore(structured_store)

    async def connect(self) -> None:
        await self._db.ensure_schema()

    async def save(self, mission: Mission) -> None:
        mission.sync_task_lists()
        await self._db.save(mission)

    async def get(self, mission_id: str) -> Mission | None:
        return await self._db.get(mission_id)

    async def list_all(self, *, limit: int = 100) -> list[Mission]:
        return await self._db.list_missions(limit=limit)

    async def list_active(self) -> list[Mission]:
        return await self._db.list_resumable()

    async def save_checkpoint(self, mission_id: str, payload: dict) -> None:
        await self._db.save_checkpoint(mission_id, payload)

    async def list_checkpoints(self, mission_id: str, limit: int = 20) -> list[dict]:
        return await self._db.list_checkpoints(mission_id, limit=limit)
