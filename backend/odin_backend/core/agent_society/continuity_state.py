"""Agent continuity checkpoints."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import aiosqlite

_SCHEMA = """
CREATE TABLE IF NOT EXISTS odin_agent_continuity (
    agent_id TEXT PRIMARY KEY,
    thought_context TEXT NOT NULL DEFAULT '{}',
    working_memory TEXT NOT NULL DEFAULT '{}',
    active_objectives TEXT NOT NULL DEFAULT '[]',
    checkpoint_at TEXT NOT NULL
);
"""


class ContinuityState:
    def __init__(self, settings: Any) -> None:
        self._path = settings.database_url.replace("sqlite+aiosqlite:///", "")
        self._db: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        self._db = await aiosqlite.connect(self._path)
        await self._db.executescript(_SCHEMA)
        await self._db.commit()

    async def disconnect(self) -> None:
        if self._db:
            await self._db.close()
            self._db = None

    async def checkpoint(self, agent_id: str, *, thought: dict, memory: dict, objectives: list[str]) -> None:
        if not self._db:
            return
        now = datetime.now(timezone.utc).isoformat()
        await self._db.execute(
            "INSERT OR REPLACE INTO odin_agent_continuity VALUES (?,?,?,?,?)",
            (agent_id, json.dumps(thought), json.dumps(memory), json.dumps(objectives), now),
        )
        await self._db.commit()

    async def restore(self, agent_id: str) -> dict[str, Any] | None:
        if not self._db:
            return None
        async with self._db.execute(
            "SELECT thought_context, working_memory, active_objectives, checkpoint_at FROM odin_agent_continuity WHERE agent_id=?",
            (agent_id,),
        ) as cur:
            row = await cur.fetchone()
        if not row:
            return None
        return {
            "thought_context": json.loads(row[0] or "{}"),
            "working_memory": json.loads(row[1] or "{}"),
            "active_objectives": json.loads(row[2] or "[]"),
            "checkpoint_at": row[3],
        }
