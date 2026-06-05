"""Execution persistence layer."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import aiosqlite

from odin_backend.config import Settings
from odin_backend.core.execution.models import ExecutionRecord, ExecutionState
from odin_backend.core.execution.result_store import ExecutionResultStore
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)

_EXEC_SCHEMA = """
CREATE TABLE IF NOT EXISTS odin_execution_records (
    execution_id TEXT PRIMARY KEY,
    payload TEXT NOT NULL,
    mission_id TEXT,
    task_id TEXT,
    state TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_odin_exec_mission ON odin_execution_records(mission_id);
CREATE INDEX IF NOT EXISTS idx_odin_exec_state ON odin_execution_records(state);
"""

_LOG_SCHEMA = """
CREATE TABLE IF NOT EXISTS odin_execution_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id TEXT NOT NULL,
    stream TEXT NOT NULL,
    line TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_odin_exec_logs ON odin_execution_logs(execution_id, id);
"""


class SqliteExecutionStore:
    def __init__(self, settings: Settings) -> None:
        db_path = settings.database_url.replace("sqlite+aiosqlite:///", "")
        self._db_path = Path(db_path)
        self._db: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._db = await aiosqlite.connect(str(self._db_path))
        await self._db.executescript(_EXEC_SCHEMA + _LOG_SCHEMA)
        await self._db.commit()
        logger.info("sqlite_execution_store_connected", path=str(self._db_path))

    async def disconnect(self) -> None:
        if self._db:
            await self._db.close()
            self._db = None

    def _conn(self) -> aiosqlite.Connection:
        if self._db is None:
            raise RuntimeError("SqliteExecutionStore not connected")
        return self._db

    async def put(self, record: ExecutionRecord) -> None:
        now = datetime.now(timezone.utc).isoformat()
        await self._conn().execute(
            """INSERT INTO odin_execution_records
               (execution_id, payload, mission_id, task_id, state, updated_at)
               VALUES (?, ?, ?, ?, ?, ?)
               ON CONFLICT(execution_id) DO UPDATE SET
                 payload=excluded.payload,
                 mission_id=excluded.mission_id,
                 task_id=excluded.task_id,
                 state=excluded.state,
                 updated_at=excluded.updated_at""",
            (
                record.execution_id,
                record.model_dump_json(),
                record.mission_id,
                record.task_id,
                record.state.value,
                now,
            ),
        )
        await self._conn().commit()

    async def get(self, execution_id: str) -> ExecutionRecord | None:
        async with self._conn().execute(
            "SELECT payload FROM odin_execution_records WHERE execution_id=?",
            (execution_id,),
        ) as cur:
            row = await cur.fetchone()
        if not row:
            return None
        return ExecutionRecord.model_validate_json(row[0])

    async def update(self, execution_id: str, **fields: Any) -> ExecutionRecord | None:
        rec = await self.get(execution_id)
        if not rec:
            return None
        updated = rec.model_copy(update=fields)
        await self.put(updated)
        return updated

    async def list_active(self) -> list[ExecutionRecord]:
        active = {s.value for s in (
            ExecutionState.QUEUED,
            ExecutionState.ALLOCATED,
            ExecutionState.RUNNING,
            ExecutionState.WAITING,
            ExecutionState.RETRYING,
            ExecutionState.ROLLING_BACK,
        )}
        out: list[ExecutionRecord] = []
        placeholders = ",".join("?" for _ in active)
        async with self._conn().execute(
            f"SELECT payload FROM odin_execution_records WHERE state IN ({placeholders})",
            tuple(active),
        ) as cur:
            async for row in cur:
                out.append(ExecutionRecord.model_validate_json(row[0]))
        return out

    async def list_all(self, *, limit: int = 100) -> list[ExecutionRecord]:
        out: list[ExecutionRecord] = []
        async with self._conn().execute(
            "SELECT payload FROM odin_execution_records ORDER BY updated_at DESC LIMIT ?",
            (limit,),
        ) as cur:
            async for row in cur:
                out.append(ExecutionRecord.model_validate_json(row[0]))
        return out

    async def list_by_mission(self, mission_id: str) -> list[ExecutionRecord]:
        out: list[ExecutionRecord] = []
        async with self._conn().execute(
            "SELECT payload FROM odin_execution_records WHERE mission_id=? ORDER BY updated_at DESC",
            (mission_id,),
        ) as cur:
            async for row in cur:
                out.append(ExecutionRecord.model_validate_json(row[0]))
        return out

    async def append_log(self, execution_id: str, stream: str, line: str) -> None:
        await self._conn().execute(
            "INSERT INTO odin_execution_logs (execution_id, stream, line, created_at) VALUES (?, ?, ?, ?)",
            (execution_id, stream, line, datetime.now(timezone.utc).isoformat()),
        )
        await self._conn().commit()

    async def get_logs(self, execution_id: str, *, stream: str = "stdout", limit: int = 200) -> list[str]:
        out: list[str] = []
        async with self._conn().execute(
            """SELECT line FROM odin_execution_logs
               WHERE execution_id=? AND stream=? ORDER BY id DESC LIMIT ?""",
            (execution_id, stream, limit),
        ) as cur:
            async for row in cur:
                out.append(row[0])
        return list(reversed(out))


class PersistedExecutionStore(ExecutionResultStore):
    """Memory cache + SQLite durability."""

    def __init__(self, sqlite: SqliteExecutionStore) -> None:
        super().__init__()
        self._sqlite = sqlite

    async def put(self, record: ExecutionRecord) -> None:
        await super().put(record)
        await self._sqlite.put(record)

    async def update(self, execution_id: str, **fields: Any) -> ExecutionRecord | None:
        updated = await super().update(execution_id, **fields)
        if updated:
            await self._sqlite.put(updated)
        return updated

    async def hydrate(self) -> int:
        records = await self._sqlite.list_all(limit=500)
        count = 0
        for rec in records:
            await super().put(rec)
            count += 1
        return count

    async def get_logs(self, execution_id: str, *, stream: str = "stdout", limit: int = 200) -> list[str]:
        return await self._sqlite.get_logs(execution_id, stream=stream, limit=limit)
