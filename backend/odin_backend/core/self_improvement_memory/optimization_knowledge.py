from __future__ import annotations
import json

class OptimizationKnowledge:
    def __init__(self, conn) -> None:
        self._conn = conn

    async def ensure(self) -> None:
        await self._conn.execute(
            "CREATE TABLE IF NOT EXISTS optimization_knowledge (id INTEGER PRIMARY KEY, payload TEXT)"
        )
        await self._conn.commit()

    async def remember(self, key: str, value: dict) -> None:
        await self._conn.execute(
            "INSERT INTO optimization_knowledge (payload) VALUES (?)",
            (json.dumps({"key": key, **value}),),
        )
        await self._conn.commit()
