"""Long-horizon objective chains."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import aiosqlite

_SCHEMA = """
CREATE TABLE IF NOT EXISTS odin_society_objectives (
    objective_id TEXT PRIMARY KEY,
    owner_agent_id TEXT NOT NULL,
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    parent_id TEXT,
    milestones TEXT NOT NULL DEFAULT '[]',
    deferred_until TEXT,
    metadata TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""


class ObjectiveChains:
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

    async def create(self, *, owner_agent_id: str, title: str, parent_id: str | None = None) -> dict[str, Any]:
        oid = str(uuid4())
        now = datetime.now(timezone.utc).isoformat()
        entry = {
            "objective_id": oid,
            "owner_agent_id": owner_agent_id,
            "title": title,
            "status": "active",
            "parent_id": parent_id,
            "milestones": [],
            "created_at": now,
            "updated_at": now,
        }
        if self._db:
            await self._db.execute(
                "INSERT INTO odin_society_objectives VALUES (?,?,?,?,?,?,?,?,?,?)",
                (oid, owner_agent_id, title, "active", parent_id, "[]", None, "{}", now, now),
            )
            await self._db.commit()
        return entry

    async def list_for_agent(self, agent_id: str) -> list[dict[str, Any]]:
        if not self._db:
            return []
        out: list[dict] = []
        async with self._db.execute(
            "SELECT objective_id, title, status, parent_id, milestones, deferred_until FROM odin_society_objectives WHERE owner_agent_id=?",
            (agent_id,),
        ) as cur:
            async for row in cur:
                out.append(
                    {
                        "objective_id": row[0],
                        "title": row[1],
                        "status": row[2],
                        "parent_id": row[3],
                        "milestones": json.loads(row[4] or "[]"),
                        "deferred_until": row[5],
                    }
                )
        return out

    async def list_all(self, *, limit: int = 50) -> list[dict[str, Any]]:
        if not self._db:
            return []
        out: list[dict] = []
        async with self._db.execute(
            "SELECT objective_id, owner_agent_id, title, status FROM odin_society_objectives ORDER BY updated_at DESC LIMIT ?",
            (limit,),
        ) as cur:
            async for row in cur:
                out.append({"objective_id": row[0], "owner_agent_id": row[1], "title": row[2], "status": row[3]})
        return out
