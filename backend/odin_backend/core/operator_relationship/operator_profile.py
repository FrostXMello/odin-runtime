"""Operator profile persistence."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import aiosqlite

_SCHEMA = """
CREATE TABLE IF NOT EXISTS odin_operator_profiles (
    operator_id TEXT PRIMARY KEY,
    profile_json TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""


class OperatorProfileStore:
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

    async def save(self, operator_id: str, profile: dict) -> dict[str, Any]:
        if not self._db:
            return profile
        now = datetime.now(timezone.utc).isoformat()
        await self._db.execute(
            "INSERT OR REPLACE INTO odin_operator_profiles VALUES (?,?,?)",
            (operator_id, json.dumps(profile), now),
        )
        await self._db.commit()
        return profile

    async def get(self, operator_id: str) -> dict[str, Any] | None:
        if not self._db:
            return None
        async with self._db.execute("SELECT profile_json FROM odin_operator_profiles WHERE operator_id=?", (operator_id,)) as cur:
            row = await cur.fetchone()
        return json.loads(row[0]) if row else None
