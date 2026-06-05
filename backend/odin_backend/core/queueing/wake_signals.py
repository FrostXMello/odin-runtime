"""Deduped wake signal persistence."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import aiosqlite

from odin_backend.config import Settings
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS odin_wake_signals (
    signal_id TEXT PRIMARY KEY,
    mission_id TEXT NOT NULL,
    reason TEXT NOT NULL,
    dedup_key TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL,
    processed_at TEXT
);
"""


class WakeSignalStore:
    """Idempotent wake signal recording — suppress duplicate wakes within window."""

    def __init__(self, settings: Settings, *, dedup_window_seconds: float = 2.0) -> None:
        self._settings = settings
        self._window = dedup_window_seconds
        db_path = settings.database_url.replace("sqlite+aiosqlite:///", "")
        self._db_path = db_path
        self._db: aiosqlite.Connection | None = None
        self._memory_seen: dict[str, float] = {}
        self._suppressed = 0

    async def connect(self) -> None:
        if not self._settings.queue_persist_enabled:
            return
        self._db = await aiosqlite.connect(self._db_path)
        await self._db.executescript(_SCHEMA)
        await self._db.commit()

    async def disconnect(self) -> None:
        if self._db:
            await self._db.close()
            self._db = None

    async def should_wake(self, mission_id: str, *, reason: str = "runtime_event") -> bool:
        import time

        key = f"wake:{mission_id}:{reason}"
        now_mono = time.monotonic()
        last = self._memory_seen.get(key, 0.0)
        if now_mono - last < self._window:
            self._suppressed += 1
            return False
        self._memory_seen[key] = now_mono

        if not self._db:
            return True

        dedup_key = key
        cutoff = (datetime.now(timezone.utc) - timedelta(seconds=self._window)).isoformat()
        async with self._db.execute(
            "SELECT signal_id FROM odin_wake_signals WHERE dedup_key=? AND created_at >= ?",
            (dedup_key, cutoff),
        ) as cur:
            if await cur.fetchone():
                self._suppressed += 1
                return False

        await self._db.execute(
            """INSERT OR IGNORE INTO odin_wake_signals
               (signal_id, mission_id, reason, dedup_key, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (str(uuid4()), mission_id, reason, dedup_key, datetime.now(timezone.utc).isoformat()),
        )
        await self._db.commit()
        return True

    @property
    def replay_suppressed(self) -> int:
        return self._suppressed

    def metrics(self) -> dict[str, Any]:
        return {"replay_suppressed": self._suppressed}
