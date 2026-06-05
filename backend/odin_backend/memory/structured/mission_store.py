"""SQLite persistence for persistent missions."""

import json
from datetime import datetime, timezone
from typing import Any

from odin_backend.models.mission import Mission, MissionLifecycle
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class MissionStructuredStore:
    """Mission tables on the shared structured SQLite database."""

    def __init__(self, structured_store: Any) -> None:
        self._store = structured_store

    def _conn(self):
        return self._store._conn()

    async def ensure_schema(self) -> None:
        await self._conn().executescript("""
            CREATE TABLE IF NOT EXISTS missions (
                mission_id TEXT PRIMARY KEY,
                objective TEXT NOT NULL,
                payload TEXT NOT NULL,
                current_state TEXT NOT NULL,
                priority INTEGER NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS mission_checkpoints (
                id TEXT PRIMARY KEY,
                mission_id TEXT NOT NULL,
                label TEXT NOT NULL,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_missions_state ON missions(current_state);
            CREATE INDEX IF NOT EXISTS idx_mission_ckpt ON mission_checkpoints(mission_id);
        """)
        await self._conn().commit()

    async def save(self, mission: Mission) -> None:
        now = datetime.now(timezone.utc).isoformat()
        payload = mission.model_dump(mode="json")
        await self._conn().execute(
            """INSERT INTO missions (mission_id, objective, payload, current_state, priority, updated_at)
               VALUES (?, ?, ?, ?, ?, ?)
               ON CONFLICT(mission_id) DO UPDATE SET
                 objective=excluded.objective,
                 payload=excluded.payload,
                 current_state=excluded.current_state,
                 priority=excluded.priority,
                 updated_at=excluded.updated_at""",
            (
                mission.mission_id,
                mission.objective,
                json.dumps(payload),
                mission.current_state.value,
                mission.priority,
                now,
            ),
        )
        await self._conn().commit()

    async def get(self, mission_id: str) -> Mission | None:
        async with self._conn().execute(
            "SELECT payload FROM missions WHERE mission_id = ?", (mission_id,)
        ) as cursor:
            row = await cursor.fetchone()
        if not row:
            return None
        return Mission.model_validate(json.loads(row[0]))

    async def list_missions(
        self,
        *,
        state: MissionLifecycle | None = None,
        limit: int = 100,
    ) -> list[Mission]:
        if state:
            query = (
                "SELECT payload FROM missions WHERE current_state = ? "
                "ORDER BY priority DESC, updated_at DESC LIMIT ?"
            )
            params: tuple[Any, ...] = (state.value, limit)
        else:
            query = "SELECT payload FROM missions ORDER BY priority DESC, updated_at DESC LIMIT ?"
            params = (limit,)
        async with self._conn().execute(query, params) as cursor:
            rows = await cursor.fetchall()
        return [Mission.model_validate(json.loads(r[0])) for r in rows]

    async def list_resumable(self) -> list[Mission]:
        active_states = (
            MissionLifecycle.QUEUED.value,
            MissionLifecycle.PLANNING.value,
            MissionLifecycle.PLANNED.value,
            MissionLifecycle.DISPATCHED.value,
            MissionLifecycle.RUNNING.value,
            MissionLifecycle.BLOCKED.value,
            MissionLifecycle.RETRYING.value,
            MissionLifecycle.ESCALATED.value,
            MissionLifecycle.APPROVAL_REQUIRED.value,
            # legacy
            MissionLifecycle.ACTIVE.value,
            MissionLifecycle.WAITING.value,
            MissionLifecycle.CREATED.value,
        )
        placeholders = ",".join("?" for _ in active_states)
        query = (
            f"SELECT payload FROM missions WHERE current_state IN ({placeholders}) "
            "ORDER BY priority DESC, updated_at DESC"
        )
        async with self._conn().execute(query, active_states) as cursor:
            rows = await cursor.fetchall()
        return [Mission.model_validate(json.loads(r[0])) for r in rows]

    async def save_checkpoint(self, mission_id: str, checkpoint: dict[str, Any]) -> None:
        now = datetime.now(timezone.utc).isoformat()
        await self._conn().execute(
            """INSERT INTO mission_checkpoints (id, mission_id, label, payload, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (
                checkpoint["id"],
                mission_id,
                checkpoint.get("label", "checkpoint"),
                json.dumps(checkpoint),
                now,
            ),
        )
        await self._conn().commit()

    async def list_checkpoints(self, mission_id: str, limit: int = 20) -> list[dict[str, Any]]:
        async with self._conn().execute(
            "SELECT payload FROM mission_checkpoints WHERE mission_id = ? "
            "ORDER BY created_at DESC LIMIT ?",
            (mission_id, limit),
        ) as cursor:
            rows = await cursor.fetchall()
        return [json.loads(r[0]) for r in rows]
