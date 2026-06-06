from __future__ import annotations
import json
from typing import Any

class ArchitectureDecisions:
    def __init__(self, conn) -> None:
        self._conn = conn

    async def ensure(self) -> None:
        await self._conn.execute(
            "CREATE TABLE IF NOT EXISTS architecture_decisions (id INTEGER PRIMARY KEY, payload TEXT)"
        )
        await self._conn.commit()

    async def record(self, decision: dict[str, Any]) -> None:
        await self._conn.execute("INSERT INTO architecture_decisions (payload) VALUES (?)", (json.dumps(decision),))
        await self._conn.commit()

    async def timeline(self, limit: int = 50) -> list[dict]:
        cur = await self._conn.execute(
            "SELECT payload FROM architecture_decisions ORDER BY id DESC LIMIT ?", (limit,)
        )
        rows = await cur.fetchall()
        return [json.loads(r[0]) for r in rows]
