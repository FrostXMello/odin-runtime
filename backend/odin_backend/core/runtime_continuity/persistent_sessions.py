"""SQLite persistence for runtime sessions."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import aiosqlite

_SCHEMA = """
CREATE TABLE IF NOT EXISTS odin_runtime_sessions (
    session_id TEXT PRIMARY KEY,
    operator_id TEXT NOT NULL,
    state_json TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""


class PersistentSessionStore:
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

    async def save(self, *, operator_id: str, state: dict, session_id: str | None = None) -> dict[str, Any]:
        if not self._db:
            return state
        sid = session_id or str(uuid4())
        now = datetime.now(timezone.utc).isoformat()
        await self._db.execute(
            "INSERT OR REPLACE INTO odin_runtime_sessions VALUES (?,?,?,?,?,?)",
            (sid, operator_id, json.dumps(state), "active", now, now),
        )
        await self._db.commit()
        return {"session_id": sid, "operator_id": operator_id, **state}

    async def list_active(self, limit: int = 50) -> list[dict[str, Any]]:
        if not self._db:
            return []
        out = []
        async with self._db.execute(
            "SELECT session_id, operator_id, state_json FROM odin_runtime_sessions WHERE status='active' LIMIT ?",
            (limit,),
        ) as cur:
            async for row in cur:
                s = json.loads(row[2])
                s["session_id"] = row[0]
                s["operator_id"] = row[1]
                out.append(s)
        return out
