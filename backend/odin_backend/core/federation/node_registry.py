"""SQLite node registry for federation."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import aiosqlite

from odin_backend.core.federation.node_identity import NodeIdentity

_SCHEMA = """
CREATE TABLE IF NOT EXISTS odin_federation_nodes (
    node_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    profile_json TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""


class NodeRegistry:
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

    async def save(self, identity: NodeIdentity) -> dict[str, Any]:
        if not self._db:
            return identity.model_dump(mode="json")
        data = identity.model_dump(mode="json")
        now = datetime.now(timezone.utc).isoformat()
        await self._db.execute(
            "INSERT OR REPLACE INTO odin_federation_nodes VALUES (?,?,?,?,?,?,?)",
            (
                identity.node_id,
                identity.name,
                identity.role,
                json.dumps(data),
                identity.status,
                data.get("created_at", now),
                now,
            ),
        )
        await self._db.commit()
        return data

    async def get(self, node_id: str) -> dict[str, Any] | None:
        if not self._db:
            return None
        async with self._db.execute(
            "SELECT profile_json, status FROM odin_federation_nodes WHERE node_id=?",
            (node_id,),
        ) as cur:
            row = await cur.fetchone()
        if not row:
            return None
        profile = json.loads(row[0])
        profile["status"] = row[1]
        return profile

    async def list_all(self, *, status: str | None = "active", limit: int = 50) -> list[dict[str, Any]]:
        if not self._db:
            return []
        out: list[dict] = []
        if status:
            q = "SELECT profile_json FROM odin_federation_nodes WHERE status=? ORDER BY updated_at DESC LIMIT ?"
            params = (status, limit)
        else:
            q = "SELECT profile_json FROM odin_federation_nodes ORDER BY updated_at DESC LIMIT ?"
            params = (limit,)
        async with self._db.execute(q, params) as cur:
            async for row in cur:
                out.append(json.loads(row[0]))
        return out

    async def update_status(self, node_id: str, status: str) -> None:
        if not self._db:
            return
        node = await self.get(node_id)
        if not node:
            return
        node["status"] = status
        node["updated_at"] = datetime.now(timezone.utc).isoformat()
        identity = NodeIdentity.model_validate(node)
        await self.save(identity)
