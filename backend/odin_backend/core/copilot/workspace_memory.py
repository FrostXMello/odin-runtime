"""Persistent workspace memory and pattern recognition."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import aiosqlite

_SCHEMA = """
CREATE TABLE IF NOT EXISTS odin_workspace_memory (
    entry_id TEXT PRIMARY KEY,
    pattern_kind TEXT NOT NULL,
    label TEXT NOT NULL,
    metadata TEXT NOT NULL DEFAULT '{}',
    occurrence_count INTEGER NOT NULL DEFAULT 1,
    updated_at TEXT NOT NULL
);
"""


class WorkspaceMemoryStore:
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

    async def record_pattern(self, *, kind: str, label: str, metadata: dict | None = None) -> None:
        if not self._db:
            return
        from uuid import uuid4

        eid = str(uuid4())
        now = datetime.now(timezone.utc).isoformat()
        async with self._db.execute(
            "SELECT entry_id, occurrence_count FROM odin_workspace_memory WHERE pattern_kind=? AND label=?",
            (kind, label),
        ) as cur:
            row = await cur.fetchone()
        if row:
            await self._db.execute(
                "UPDATE odin_workspace_memory SET occurrence_count=?, updated_at=?, metadata=? WHERE entry_id=?",
                (row[1] + 1, now, json.dumps(metadata or {}), row[0]),
            )
        else:
            await self._db.execute(
                "INSERT INTO odin_workspace_memory (entry_id, pattern_kind, label, metadata, occurrence_count, updated_at) VALUES (?,?,?,?,?,?)",
                (eid, kind, label, json.dumps(metadata or {}), 1, now),
            )
        await self._db.commit()

    async def list_patterns(self, *, limit: int = 30) -> list[dict[str, Any]]:
        if not self._db:
            return []
        out: list[dict] = []
        async with self._db.execute(
            "SELECT pattern_kind, label, occurrence_count, metadata, updated_at FROM odin_workspace_memory ORDER BY occurrence_count DESC LIMIT ?",
            (limit,),
        ) as cur:
            async for row in cur:
                out.append(
                    {
                        "kind": row[0],
                        "label": row[1],
                        "count": row[2],
                        "metadata": json.loads(row[3] or "{}"),
                        "updated_at": row[4],
                    }
                )
        return out
