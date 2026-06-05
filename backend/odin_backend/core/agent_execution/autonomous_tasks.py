"""Long-running autonomous delegated tasks."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import aiosqlite

_SCHEMA = """
CREATE TABLE IF NOT EXISTS odin_agent_tasks (
    task_id TEXT PRIMARY KEY,
    owner_agent_id TEXT NOT NULL,
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    payload_json TEXT NOT NULL DEFAULT '{}',
    mission_id TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""


class AutonomousTaskStore:
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

    async def create(self, *, owner_agent_id: str, title: str, mission_id: str | None = None, payload: dict | None = None) -> dict[str, Any]:
        if not self._db:
            return {"title": title}
        tid = str(uuid4())
        now = datetime.now(timezone.utc).isoformat()
        await self._db.execute(
            "INSERT INTO odin_agent_tasks VALUES (?,?,?,?,?,?,?,?)",
            (tid, owner_agent_id, title, "pending", json.dumps(payload or {}), mission_id, now, now),
        )
        await self._db.commit()
        return {"task_id": tid, "owner_agent_id": owner_agent_id, "title": title, "status": "pending"}

    async def list_for_agent(self, agent_id: str) -> list[dict[str, Any]]:
        if not self._db:
            return []
        out = []
        async with self._db.execute(
            "SELECT task_id, title, status, mission_id FROM odin_agent_tasks WHERE owner_agent_id=?",
            (agent_id,),
        ) as cur:
            async for row in cur:
                out.append({"task_id": row[0], "title": row[1], "status": row[2], "mission_id": row[3]})
        return out

    async def list_pending(self) -> list[dict[str, Any]]:
        if not self._db:
            return []
        out = []
        async with self._db.execute("SELECT task_id, owner_agent_id, title FROM odin_agent_tasks WHERE status='pending'") as cur:
            async for row in cur:
                out.append({"task_id": row[0], "owner_agent_id": row[1], "title": row[2]})
        return out
