"""Persistent world state store."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import aiosqlite

_SCHEMA = """
CREATE TABLE IF NOT EXISTS odin_world_entities (
    entity_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    kind TEXT NOT NULL,
    data_json TEXT NOT NULL,
    confidence REAL NOT NULL DEFAULT 0.5,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS odin_world_relationships (
    rel_id TEXT PRIMARY KEY,
    from_entity TEXT NOT NULL,
    to_entity TEXT NOT NULL,
    kind TEXT NOT NULL,
    confidence REAL NOT NULL DEFAULT 0.5,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS odin_world_timelines (
    timeline_id TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    events_json TEXT NOT NULL,
    confidence REAL NOT NULL DEFAULT 0.5,
    updated_at TEXT NOT NULL
);
"""


class WorldStateStore:
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

    async def upsert_entity(self, *, name: str, kind: str, data: dict, confidence: float = 0.5) -> dict[str, Any]:
        if not self._db:
            return {"name": name, "kind": kind}
        eid = str(uuid4())
        now = datetime.now(timezone.utc).isoformat()
        await self._db.execute(
            "INSERT OR REPLACE INTO odin_world_entities VALUES (?,?,?,?,?,?)",
            (eid, name, kind, json.dumps(data), confidence, now),
        )
        await self._db.commit()
        return {"entity_id": eid, "name": name, "kind": kind, "confidence": confidence}

    async def add_relationship(self, *, from_entity: str, to_entity: str, kind: str, confidence: float = 0.5) -> dict:
        if not self._db:
            return {}
        rid = str(uuid4())
        now = datetime.now(timezone.utc).isoformat()
        await self._db.execute(
            "INSERT INTO odin_world_relationships VALUES (?,?,?,?,?,?)",
            (rid, from_entity, to_entity, kind, confidence, now),
        )
        await self._db.commit()
        return {"rel_id": rid, "from": from_entity, "to": to_entity, "kind": kind}

    async def list_entities(self, limit: int = 50) -> list[dict[str, Any]]:
        if not self._db:
            return []
        out = []
        async with self._db.execute(
            "SELECT entity_id, name, kind, data_json, confidence FROM odin_world_entities ORDER BY updated_at DESC LIMIT ?",
            (limit,),
        ) as cur:
            async for row in cur:
                out.append({
                    "entity_id": row[0], "name": row[1], "kind": row[2],
                    "data": json.loads(row[3]), "confidence": row[4],
                })
        return out

    async def list_relationships(self, limit: int = 50) -> list[dict[str, Any]]:
        if not self._db:
            return []
        out = []
        async with self._db.execute(
            "SELECT rel_id, from_entity, to_entity, kind, confidence FROM odin_world_relationships LIMIT ?",
            (limit,),
        ) as cur:
            async for row in cur:
                out.append({"rel_id": row[0], "from": row[1], "to": row[2], "kind": row[3], "confidence": row[4]})
        return out
