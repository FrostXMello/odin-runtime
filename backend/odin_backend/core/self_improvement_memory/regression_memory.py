from __future__ import annotations
import json

class RegressionMemory:
    def __init__(self, conn) -> None:
        self._conn = conn

    async def ensure(self) -> None:
        await self._conn.execute(
            "CREATE TABLE IF NOT EXISTS regression_memory (id INTEGER PRIMARY KEY, payload TEXT)"
        )
        await self._conn.commit()

    async def record(self, regression: dict) -> None:
        await self._conn.execute("INSERT INTO regression_memory (payload) VALUES (?)", (json.dumps(regression),))
        await self._conn.commit()
