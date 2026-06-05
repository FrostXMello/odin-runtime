"""Persistent macro storage."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import aiosqlite

_SCHEMA = """
CREATE TABLE IF NOT EXISTS odin_workflow_macros (
    macro_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    steps TEXT NOT NULL DEFAULT '[]',
    parameters TEXT NOT NULL DEFAULT '[]',
    version INTEGER NOT NULL DEFAULT 1,
    updated_at TEXT NOT NULL
);
"""


class WorkflowMemoryStore:
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

    async def save(self, macro: dict[str, Any]) -> None:
        if not self._db:
            return
        now = datetime.now(timezone.utc).isoformat()
        await self._db.execute(
            "INSERT OR REPLACE INTO odin_workflow_macros (macro_id, name, steps, parameters, version, updated_at) VALUES (?,?,?,?,?,?)",
            (
                macro["id"],
                macro["name"],
                json.dumps(macro.get("steps", [])),
                json.dumps(macro.get("parameters", [])),
                macro.get("version", 1),
                now,
            ),
        )
        await self._db.commit()

    async def list_macros(self, *, limit: int = 30) -> list[dict[str, Any]]:
        if not self._db:
            return []
        out: list[dict] = []
        async with self._db.execute(
            "SELECT macro_id, name, steps, parameters, version, updated_at FROM odin_workflow_macros ORDER BY updated_at DESC LIMIT ?",
            (limit,),
        ) as cur:
            async for row in cur:
                out.append(
                    {
                        "id": row[0],
                        "name": row[1],
                        "steps": json.loads(row[2] or "[]"),
                        "parameters": json.loads(row[3] or "[]"),
                        "version": row[4],
                        "updated_at": row[5],
                    }
                )
        return out
