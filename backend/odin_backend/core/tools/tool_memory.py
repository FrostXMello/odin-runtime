"""Tool selection memory — lightweight SQLite-backed preferences."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import aiosqlite

from odin_backend.config import Settings


class ToolMemory:
    def __init__(self, settings: Settings) -> None:
        db_path = settings.database_url.replace("sqlite+aiosqlite:///", "")
        self._db_path = db_path
        self._db: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        self._db = await aiosqlite.connect(self._db_path)
        await self._db.executescript(
            """
            CREATE TABLE IF NOT EXISTS odin_tool_memory (
                mission_id TEXT,
                capability TEXT,
                tool_name TEXT,
                success INTEGER NOT NULL DEFAULT 1,
                score REAL NOT NULL DEFAULT 0.5,
                metadata TEXT NOT NULL DEFAULT '{}',
                updated_at TEXT NOT NULL,
                PRIMARY KEY (mission_id, capability, tool_name)
            );
            """
        )
        await self._db.commit()

    async def disconnect(self) -> None:
        if self._db:
            await self._db.close()
            self._db = None

    async def record(
        self,
        mission_id: str,
        capability: str,
        tool_name: str,
        *,
        success: bool = True,
    ) -> None:
        if not self._db:
            return
        from datetime import datetime, timezone

        score = 0.7 if success else 0.2
        now = datetime.now(timezone.utc).isoformat()
        await self._db.execute(
            """INSERT INTO odin_tool_memory
               (mission_id, capability, tool_name, success, score, updated_at)
               VALUES (?, ?, ?, ?, ?, ?)
               ON CONFLICT(mission_id, capability, tool_name) DO UPDATE SET
                 success=excluded.success,
                 score=CASE WHEN excluded.success=1 THEN MIN(0.99, odin_tool_memory.score + 0.05)
                            ELSE MAX(0.05, odin_tool_memory.score - 0.1) END,
                 updated_at=excluded.updated_at""",
            (mission_id, capability, tool_name, 1 if success else 0, score, now),
        )
        await self._db.commit()

    async def bias_for_capability(self, capability: str, *, limit: int = 10) -> dict[str, float]:
        if not self._db:
            return {}
        bias: dict[str, float] = {}
        async with self._db.execute(
            """SELECT tool_name, AVG(score) FROM odin_tool_memory
               WHERE capability=? GROUP BY tool_name ORDER BY AVG(score) DESC LIMIT ?""",
            (capability, limit),
        ) as cur:
            async for row in cur:
                bias[row[0]] = float(row[1])
        return bias
