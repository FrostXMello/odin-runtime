"""Mission execution history index for planner retrieval."""

from __future__ import annotations

import json
from typing import Any

import aiosqlite

from odin_backend.config import Settings


class ExecutionHistoryIndex:
    def __init__(self, settings: Settings) -> None:
        self._db_path = settings.database_url.replace("sqlite+aiosqlite:///", "")
        self._db: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        self._db = await aiosqlite.connect(self._db_path)
        await self._db.executescript(
            """
            CREATE TABLE IF NOT EXISTS odin_planner_history (
                record_id TEXT PRIMARY KEY,
                mission_id TEXT NOT NULL,
                event TEXT NOT NULL,
                capability TEXT,
                tool_name TEXT,
                success INTEGER NOT NULL DEFAULT 1,
                summary TEXT NOT NULL,
                metadata TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_planner_hist_mission ON odin_planner_history(mission_id);
            """
        )
        await self._db.commit()

    async def disconnect(self) -> None:
        if self._db:
            await self._db.close()
            self._db = None

    async def append(
        self,
        mission_id: str,
        event: str,
        summary: str,
        *,
        capability: str | None = None,
        tool_name: str | None = None,
        success: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        if not self._db:
            return
        from datetime import datetime, timezone
        from uuid import uuid4

        await self._db.execute(
            """INSERT INTO odin_planner_history
               (record_id, mission_id, event, capability, tool_name, success, summary, metadata, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                str(uuid4()),
                mission_id,
                event,
                capability,
                tool_name,
                1 if success else 0,
                summary[:2000],
                json.dumps(metadata or {}),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        await self._db.commit()

    async def list_for_mission(self, mission_id: str, *, limit: int = 50) -> list[dict[str, Any]]:
        if not self._db:
            return []
        out: list[dict[str, Any]] = []
        async with self._db.execute(
            """SELECT summary, event, capability, tool_name, success, created_at
               FROM odin_planner_history WHERE mission_id=? ORDER BY created_at DESC LIMIT ?""",
            (mission_id, limit),
        ) as cur:
            async for row in cur:
                out.append(
                    {
                        "summary": row[0],
                        "event": row[1],
                        "capability": row[2],
                        "tool_name": row[3],
                        "success": bool(row[4]),
                        "created_at": row[5],
                    }
                )
        return out

    async def failure_count(self, mission_id: str) -> int:
        if not self._db:
            return 0
        async with self._db.execute(
            "SELECT COUNT(*) FROM odin_planner_history WHERE mission_id=? AND success=0",
            (mission_id,),
        ) as cur:
            row = await cur.fetchone()
            return int(row[0]) if row else 0
