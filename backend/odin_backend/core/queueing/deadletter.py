"""Dead-letter queue management."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import aiosqlite

from odin_backend.config import Settings
from odin_backend.core.queueing.queue_models import DeadLetterItem, QueueItem
from odin_backend.core.queueing.sqlite_backend import SQLiteQueueBackend
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS odin_deadletter_items (
    deadletter_id TEXT PRIMARY KEY,
    queue_item_id TEXT NOT NULL,
    mission_id TEXT,
    reason TEXT NOT NULL,
    payload TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    replay_count INTEGER NOT NULL DEFAULT 0
);
"""


class DeadLetterQueue:
    def __init__(self, settings: Settings, backend: SQLiteQueueBackend | None = None) -> None:
        self._settings = settings
        self._backend = backend
        db_path = settings.database_url.replace("sqlite+aiosqlite:///", "")
        self._db_path = db_path
        self._db: aiosqlite.Connection | None = None
        self._count = 0

    async def connect(self) -> None:
        self._db = await aiosqlite.connect(self._db_path)
        self._db.row_factory = aiosqlite.Row
        await self._db.executescript(_SCHEMA)
        await self._db.commit()

    async def disconnect(self) -> None:
        if self._db:
            await self._db.close()
            self._db = None

    def _conn(self) -> aiosqlite.Connection:
        if self._db is None:
            raise RuntimeError("DeadLetterQueue not connected")
        return self._db

    async def record(self, item: QueueItem, *, reason: str) -> DeadLetterItem:
        dl = DeadLetterItem(
            queue_item_id=item.queue_item_id,
            reason=reason,
            payload=item.payload,
            mission_id=item.mission_id,
        )
        await self._conn().execute(
            """INSERT INTO odin_deadletter_items
               (deadletter_id, queue_item_id, mission_id, reason, payload, created_at, replay_count)
               VALUES (?, ?, ?, ?, ?, ?, 0)""",
            (
                dl.deadletter_id,
                dl.queue_item_id,
                dl.mission_id,
                dl.reason,
                json.dumps(dl.payload),
                dl.created_at.isoformat(),
            ),
        )
        await self._conn().commit()
        if self._backend:
            await self._backend.mark_deadletter(item.queue_item_id, reason=reason)
        self._count += 1
        return dl

    async def list_items(self, *, limit: int = 50) -> list[DeadLetterItem]:
        out: list[DeadLetterItem] = []
        async with self._conn().execute(
            "SELECT * FROM odin_deadletter_items ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ) as cur:
            async for row in cur:
                out.append(
                    DeadLetterItem(
                        deadletter_id=row["deadletter_id"],
                        queue_item_id=row["queue_item_id"],
                        mission_id=row["mission_id"],
                        reason=row["reason"],
                        payload=json.loads(row["payload"] or "{}"),
                        created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
                        replay_count=int(row["replay_count"]),
                    )
                )
        return out

    async def get(self, deadletter_id: str) -> DeadLetterItem | None:
        async with self._conn().execute(
            "SELECT * FROM odin_deadletter_items WHERE deadletter_id=?",
            (deadletter_id,),
        ) as cur:
            row = await cur.fetchone()
        if not row:
            return None
        return DeadLetterItem(
            deadletter_id=row["deadletter_id"],
            queue_item_id=row["queue_item_id"],
            mission_id=row["mission_id"],
            reason=row["reason"],
            payload=json.loads(row["payload"] or "{}"),
            created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
            replay_count=int(row["replay_count"]),
        )

    async def replay(self, deadletter_id: str) -> QueueItem | None:
        dl = await self.get(deadletter_id)
        if not dl or not self._backend:
            return None
        item = await self._backend.replay_item(dl.queue_item_id)
        if item:
            await self._conn().execute(
                "UPDATE odin_deadletter_items SET replay_count=replay_count+1 WHERE deadletter_id=?",
                (deadletter_id,),
            )
            await self._conn().commit()
        return item

    @property
    def count(self) -> int:
        return self._count
