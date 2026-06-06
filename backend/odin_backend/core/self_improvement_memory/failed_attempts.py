from __future__ import annotations
import json
from typing import Any

class FailedAttempts:
    def __init__(self, conn) -> None:
        self._conn = conn

    async def ensure(self) -> None:
        await self._conn.execute(
            "CREATE TABLE IF NOT EXISTS failed_attempts (id INTEGER PRIMARY KEY, payload TEXT)"
        )
        await self._conn.commit()

    async def record(self, attempt: dict[str, Any]) -> None:
        await self._conn.execute("INSERT INTO failed_attempts (payload) VALUES (?)", (json.dumps(attempt),))
        await self._conn.commit()
