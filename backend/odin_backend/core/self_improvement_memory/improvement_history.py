from __future__ import annotations
import json
from typing import Any

class ImprovementHistory:
    def __init__(self, conn) -> None:
        self._conn = conn

    async def ensure(self) -> None:
        await self._conn.execute(
            "CREATE TABLE IF NOT EXISTS improvement_history (id INTEGER PRIMARY KEY, payload TEXT, created_at REAL)"
        )
        await self._conn.commit()

    async def add(self, entry: dict[str, Any]) -> None:
        await self._conn.execute(
            "INSERT INTO improvement_history (payload, created_at) VALUES (?, ?)",
            (json.dumps(entry), entry.get("created_at", 0)),
        )
        await self._conn.commit()

    async def recent(self, limit: int = 20) -> list[dict]:
        cur = await self._conn.execute(
            "SELECT payload FROM improvement_history ORDER BY id DESC LIMIT ?", (limit,)
        )
        rows = await cur.fetchall()
        return [json.loads(r[0]) for r in rows]
