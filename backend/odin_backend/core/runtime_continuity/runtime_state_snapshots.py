"""Runtime behavioral state snapshots."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import aiosqlite

_SCHEMA = """
CREATE TABLE IF NOT EXISTS odin_runtime_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    kind TEXT NOT NULL,
    state_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


class RuntimeStateSnapshots:
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

    async def capture(self, *, kind: str, state: dict) -> dict[str, Any]:
        if not self._db:
            return state
        sid = str(uuid4())
        now = datetime.now(timezone.utc).isoformat()
        await self._db.execute(
            "INSERT INTO odin_runtime_snapshots VALUES (?,?,?,?)",
            (sid, kind, json.dumps(state), now),
        )
        await self._db.commit()
        return {"snapshot_id": sid, "kind": kind, "created_at": now}

    async def latest(self, kind: str) -> dict[str, Any] | None:
        if not self._db:
            return None
        async with self._db.execute(
            "SELECT state_json, created_at FROM odin_runtime_snapshots WHERE kind=? ORDER BY created_at DESC LIMIT 1",
            (kind,),
        ) as cur:
            row = await cur.fetchone()
        if not row:
            return None
        state = json.loads(row[0])
        state["created_at"] = row[1]
        return state
