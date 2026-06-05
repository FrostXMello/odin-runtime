"""SQLite structured memory."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import aiosqlite

from odin_backend.config import Settings
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class StructuredStore:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        db_path = settings.database_url.replace("sqlite+aiosqlite:///", "")
        self._db_path = Path(db_path)
        self._db: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._db = await aiosqlite.connect(str(self._db_path))
        await self._db.executescript("""
            CREATE TABLE IF NOT EXISTS preferences (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS workflow_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_id TEXT NOT NULL,
                event TEXT NOT NULL,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS agent_states (
                agent_id TEXT PRIMARY KEY,
                state TEXT NOT NULL,
                payload TEXT,
                updated_at TEXT NOT NULL
            );
        """)
        await self._db.commit()
        logger.info("structured_memory_connected", path=str(self._db_path))

    async def disconnect(self) -> None:
        if self._db:
            await self._db.close()
            self._db = None

    def _conn(self) -> aiosqlite.Connection:
        if self._db is None:
            raise RuntimeError("StructuredStore not connected")
        return self._db

    async def get_preference(self, key: str, default: Any = None) -> Any:
        async with self._conn().execute(
            "SELECT value FROM preferences WHERE key = ?", (key,)
        ) as cursor:
            row = await cursor.fetchone()
        if not row:
            return default
        return json.loads(row[0])

    async def set_preference(self, key: str, value: Any) -> None:
        now = datetime.now(timezone.utc).isoformat()
        await self._conn().execute(
            """INSERT INTO preferences (key, value, updated_at) VALUES (?, ?, ?)
               ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at""",
            (key, json.dumps(value), now),
        )
        await self._conn().commit()

    async def log_workflow_event(self, workflow_id: str, event: str, payload: dict) -> None:
        now = datetime.now(timezone.utc).isoformat()
        await self._conn().execute(
            "INSERT INTO workflow_events (workflow_id, event, payload, created_at) VALUES (?, ?, ?, ?)",
            (workflow_id, event, json.dumps(payload), now),
        )
        await self._conn().commit()

    async def get_workflow_history(self, workflow_id: str) -> list[dict]:
        async with self._conn().execute(
            "SELECT event, payload, created_at FROM workflow_events WHERE workflow_id = ? ORDER BY id",
            (workflow_id,),
        ) as cursor:
            rows = await cursor.fetchall()
        return [
            {"event": r[0], "payload": json.loads(r[1]), "created_at": r[2]} for r in rows
        ]

    async def set_agent_state(self, agent_id: str, state: str, payload: dict | None = None) -> None:
        now = datetime.now(timezone.utc).isoformat()
        await self._conn().execute(
            """INSERT INTO agent_states (agent_id, state, payload, updated_at) VALUES (?, ?, ?, ?)
               ON CONFLICT(agent_id) DO UPDATE SET state=excluded.state, payload=excluded.payload,
               updated_at=excluded.updated_at""",
            (agent_id, state, json.dumps(payload or {}), now),
        )
        await self._conn().commit()
