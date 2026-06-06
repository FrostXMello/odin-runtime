"""SQLite cognition state store."""
from __future__ import annotations

import json
import time
from typing import Any
import aiosqlite

class SqliteTable:
    def __init__(self, conn, table: str) -> None:
        self._conn = conn
        self._table = table

    async def ensure(self) -> None:
        await self._conn.execute(
            f"CREATE TABLE IF NOT EXISTS {self._table} (id INTEGER PRIMARY KEY, payload TEXT, created_at REAL)"
        )
        await self._conn.commit()

    async def insert(self, payload: dict[str, Any]) -> None:
        await self._conn.execute(
            f"INSERT INTO {self._table} (payload, created_at) VALUES (?, ?)",
            (json.dumps(payload), payload.get("created_at", time.time())),
        )
        await self._conn.commit()

    async def recent(self, limit: int = 20) -> list[dict]:
        cur = await self._conn.execute(
            f"SELECT payload FROM {self._table} ORDER BY id DESC LIMIT ?", (limit,)
        )
        rows = await cur.fetchall()
        return [json.loads(r[0]) for r in rows]
