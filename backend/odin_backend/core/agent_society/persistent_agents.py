"""SQLite persistence for society agents."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import aiosqlite

from odin_backend.core.agent_society.agent_identity import AgentIdentity

_SCHEMA = """
CREATE TABLE IF NOT EXISTS odin_society_agents (
    agent_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    profile_json TEXT NOT NULL,
    performance_json TEXT NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'active',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS odin_society_performance (
    agent_id TEXT NOT NULL,
    metric TEXT NOT NULL,
    value REAL NOT NULL,
    recorded_at TEXT NOT NULL
);
"""


class PersistentAgentStore:
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

    async def save(self, identity: AgentIdentity, *, performance: dict | None = None) -> dict[str, Any]:
        if not self._db:
            return identity.model_dump(mode="json")
        data = identity.model_dump(mode="json")
        now = datetime.now(timezone.utc).isoformat()
        await self._db.execute(
            "INSERT OR REPLACE INTO odin_society_agents VALUES (?,?,?,?,?,?,?,?)",
            (
                identity.agent_id,
                identity.name,
                identity.role,
                json.dumps(data),
                json.dumps(performance or {}),
                identity.status,
                data.get("created_at", now),
                now,
            ),
        )
        await self._db.commit()
        return data

    async def get(self, agent_id: str) -> dict[str, Any] | None:
        if not self._db:
            return None
        async with self._db.execute(
            "SELECT profile_json, performance_json, status FROM odin_society_agents WHERE agent_id=?",
            (agent_id,),
        ) as cur:
            row = await cur.fetchone()
        if not row:
            return None
        profile = json.loads(row[0])
        profile["performance"] = json.loads(row[1] or "{}")
        profile["status"] = row[2]
        return profile

    async def list_all(self, *, status: str | None = "active", limit: int = 50) -> list[dict[str, Any]]:
        if not self._db:
            return []
        out: list[dict] = []
        if status:
            q = "SELECT profile_json, performance_json FROM odin_society_agents WHERE status=? ORDER BY updated_at DESC LIMIT ?"
            params = (status, limit)
        else:
            q = "SELECT profile_json, performance_json FROM odin_society_agents ORDER BY updated_at DESC LIMIT ?"
            params = (limit,)
        async with self._db.execute(q, params) as cur:
            async for row in cur:
                p = json.loads(row[0])
                p["performance"] = json.loads(row[1] or "{}")
                out.append(p)
        return out

    async def record_performance(self, agent_id: str, *, metric: str, value: float) -> None:
        if not self._db:
            return
        await self._db.execute(
            "INSERT INTO odin_society_performance (agent_id, metric, value, recorded_at) VALUES (?,?,?,?)",
            (agent_id, metric, value, datetime.now(timezone.utc).isoformat()),
        )
        await self._db.commit()
