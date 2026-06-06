from __future__ import annotations
import json
from typing import Any

class PatchOutcomes:
    def __init__(self, conn) -> None:
        self._conn = conn

    async def ensure(self) -> None:
        await self._conn.execute(
            "CREATE TABLE IF NOT EXISTS patch_outcomes (id INTEGER PRIMARY KEY, payload TEXT)"
        )
        await self._conn.commit()

    async def record(self, outcome: dict[str, Any]) -> None:
        await self._conn.execute("INSERT INTO patch_outcomes (payload) VALUES (?)", (json.dumps(outcome),))
        await self._conn.commit()
