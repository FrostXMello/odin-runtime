"""Persistent objective graph — SQLite-backed long-term goals."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

import aiosqlite

from odin_backend.config import Settings
from pydantic import BaseModel, Field

_SCHEMA = """
CREATE TABLE IF NOT EXISTS odin_objectives (
    objective_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'active',
    priority REAL NOT NULL DEFAULT 0.5,
    confidence REAL NOT NULL DEFAULT 0.5,
    parent_id TEXT,
    recurring INTEGER NOT NULL DEFAULT 0,
    deferred_until TEXT,
    metadata TEXT NOT NULL DEFAULT '{}',
    outcome TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_objective_status ON odin_objectives(status);
CREATE INDEX IF NOT EXISTS idx_objective_priority ON odin_objectives(priority);
"""


class ObjectiveStatus(StrEnum):
    ACTIVE = "active"
    COMPLETED = "completed"
    DEFERRED = "deferred"
    FAILED = "failed"
    RECURRING = "recurring"


class PersistentObjective(BaseModel):
    objective_id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    description: str = ""
    status: ObjectiveStatus = ObjectiveStatus.ACTIVE
    priority: float = 0.5
    confidence: float = 0.5
    parent_id: str | None = None
    recurring: bool = False
    deferred_until: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    outcome: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PersistentObjectiveGraph:
    def __init__(self, settings: Settings) -> None:
        self._path = settings.database_url.replace("sqlite+aiosqlite:///", "")
        self._db: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        self._db = await aiosqlite.connect(self._path)
        await self._db.executescript(_SCHEMA)
        await self._db.commit()
        await self._seed_defaults()

    async def disconnect(self) -> None:
        if self._db:
            await self._db.close()
            self._db = None

    async def _seed_defaults(self) -> None:
        async with self._db.execute("SELECT COUNT(*) FROM odin_objectives") as cur:
            row = await cur.fetchone()
        if row and row[0] > 0:
            return
        defaults = [
            ("Improve planner accuracy", "Analyze failed decompositions and adjust strategy weights"),
            ("Reduce execution failures", "Mine failure clusters and tune retry heuristics"),
            ("Optimize routing latency", "Profile capability performance and rebalance workers"),
            ("Consolidate mission memories", "Merge episodic memories from completed missions"),
        ]
        for title, desc in defaults:
            await self.upsert(PersistentObjective(title=title, description=desc, priority=0.6))

    async def upsert(self, obj: PersistentObjective) -> PersistentObjective:
        if not self._db:
            return obj
        obj.updated_at = datetime.now(timezone.utc)
        await self._db.execute(
            """INSERT INTO odin_objectives
               (objective_id, title, description, status, priority, confidence, parent_id,
                recurring, deferred_until, metadata, outcome, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(objective_id) DO UPDATE SET
                 title=excluded.title, description=excluded.description, status=excluded.status,
                 priority=excluded.priority, confidence=excluded.confidence,
                 metadata=excluded.metadata, outcome=excluded.outcome, updated_at=excluded.updated_at""",
            (
                obj.objective_id,
                obj.title,
                obj.description,
                obj.status.value,
                obj.priority,
                obj.confidence,
                obj.parent_id,
                1 if obj.recurring else 0,
                obj.deferred_until.isoformat() if obj.deferred_until else None,
                json.dumps(obj.metadata),
                obj.outcome,
                obj.created_at.isoformat(),
                obj.updated_at.isoformat(),
            ),
        )
        await self._db.commit()
        return obj

    async def list_objectives(self, *, status: str | None = None, limit: int = 50) -> list[PersistentObjective]:
        if not self._db:
            return []
        q = "SELECT objective_id, title, description, status, priority, confidence, parent_id, recurring, deferred_until, metadata, outcome, created_at, updated_at FROM odin_objectives"
        params: list[Any] = []
        if status:
            q += " WHERE status=?"
            params.append(status)
        q += " ORDER BY priority DESC, updated_at DESC LIMIT ?"
        params.append(limit)
        out: list[PersistentObjective] = []
        async with self._db.execute(q, params) as cur:
            async for row in cur:
                out.append(
                    PersistentObjective(
                        objective_id=row[0],
                        title=row[1],
                        description=row[2],
                        status=ObjectiveStatus(row[3]),
                        priority=row[4],
                        confidence=row[5],
                        parent_id=row[6],
                        recurring=bool(row[7]),
                        deferred_until=datetime.fromisoformat(row[8]) if row[8] else None,
                        metadata=json.loads(row[9] or "{}"),
                        outcome=row[10],
                        created_at=datetime.fromisoformat(row[11]),
                        updated_at=datetime.fromisoformat(row[12]),
                    )
                )
        return out

    async def reinforce(self, objective_id: str, *, success: bool) -> None:
        objs = await self.list_objectives(limit=200)
        obj = next((o for o in objs if o.objective_id == objective_id), None)
        if not obj:
            return
        obj.confidence = min(0.99, obj.confidence + 0.05) if success else max(0.1, obj.confidence - 0.08)
        if success:
            obj.status = ObjectiveStatus.COMPLETED
            obj.outcome = "completed"
        await self.upsert(obj)

    async def defer(self, objective_id: str, *, until: datetime | None = None) -> None:
        objs = await self.list_objectives(limit=200)
        obj = next((o for o in objs if o.objective_id == objective_id), None)
        if not obj:
            return
        obj.status = ObjectiveStatus.DEFERRED
        obj.deferred_until = until
        await self.upsert(obj)

    async def top_priority(self, limit: int = 3) -> list[PersistentObjective]:
        objs = await self.list_objectives(status=ObjectiveStatus.ACTIVE.value, limit=limit * 2)
        now = datetime.now(timezone.utc)
        viable = [o for o in objs if not o.deferred_until or o.deferred_until <= now]
        return sorted(viable, key=lambda o: -o.priority)[:limit]
