"""SQLite-backed vector persistence."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import aiosqlite

from odin_backend.config import Settings

_SCHEMA = """
CREATE TABLE IF NOT EXISTS odin_embedding_vectors (
    vector_id TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    embedding TEXT NOT NULL,
    metadata TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_embed_label ON odin_embedding_vectors(label);
"""


class VectorStore:
    def __init__(self, settings: Settings) -> None:
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

    async def upsert(self, vector_id: str, label: str, embedding: list[float], metadata: dict[str, Any] | None = None) -> None:
        if not self._db:
            return
        await self._db.execute(
            """INSERT INTO odin_embedding_vectors (vector_id, label, embedding, metadata, created_at)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(vector_id) DO UPDATE SET label=excluded.label, embedding=excluded.embedding, metadata=excluded.metadata""",
            (
                vector_id,
                label,
                json.dumps(embedding),
                json.dumps(metadata or {}),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        await self._db.commit()

    async def list_recent(self, *, limit: int = 200) -> list[dict[str, Any]]:
        if not self._db:
            return []
        out: list[dict] = []
        async with self._db.execute(
            "SELECT vector_id, label, embedding, metadata FROM odin_embedding_vectors ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ) as cur:
            async for row in cur:
                out.append(
                    {
                        "vector_id": row[0],
                        "label": row[1],
                        "embedding": json.loads(row[2]),
                        "metadata": json.loads(row[3]),
                    }
                )
        return out
