"""SQLite persistence for knowledge fabric."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import aiosqlite

_SCHEMA = """
CREATE TABLE IF NOT EXISTS odin_knowledge_nodes (
    node_id TEXT PRIMARY KEY,
    entity TEXT NOT NULL,
    fact TEXT NOT NULL,
    confidence REAL NOT NULL DEFAULT 0.5,
    source TEXT NOT NULL DEFAULT 'local',
    timestamp TEXT NOT NULL,
    supporting_evidence TEXT NOT NULL DEFAULT '[]',
    contradicting_evidence TEXT NOT NULL DEFAULT '[]',
    mission_origin TEXT,
    reasoning_chain TEXT NOT NULL DEFAULT '[]',
    metadata TEXT NOT NULL DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS odin_knowledge_relationships (
    rel_id TEXT PRIMARY KEY,
    source_entity TEXT NOT NULL,
    target_entity TEXT NOT NULL,
    relation TEXT NOT NULL,
    confidence REAL NOT NULL DEFAULT 0.5,
    timestamp TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS odin_knowledge_sources (
    source_id TEXT PRIMARY KEY,
    url TEXT NOT NULL,
    title TEXT NOT NULL DEFAULT '',
    trust_score REAL NOT NULL DEFAULT 0.5,
    fetched_at TEXT NOT NULL
);
"""


class KnowledgeStore:
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

    async def upsert_node(self, node: dict[str, Any]) -> None:
        if not self._db:
            return
        await self._db.execute(
            """INSERT OR REPLACE INTO odin_knowledge_nodes
            (node_id, entity, fact, confidence, source, timestamp, supporting_evidence,
             contradicting_evidence, mission_origin, reasoning_chain, metadata)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (
                node["id"],
                node["entity"],
                node["fact"],
                node.get("confidence", 0.5),
                node.get("source", "local"),
                node.get("timestamp", datetime.now(timezone.utc).isoformat()),
                json.dumps(node.get("supporting_evidence", [])),
                json.dumps(node.get("contradicting_evidence", [])),
                node.get("mission_origin"),
                json.dumps(node.get("reasoning_chain", [])),
                json.dumps(node.get("metadata", {})),
            ),
        )
        await self._db.commit()

    async def list_nodes(self, *, limit: int = 100, entity: str | None = None) -> list[dict[str, Any]]:
        if not self._db:
            return []
        out: list[dict] = []
        if entity:
            query = "SELECT * FROM odin_knowledge_nodes WHERE entity=? ORDER BY timestamp DESC LIMIT ?"
            params = (entity, limit)
        else:
            query = "SELECT * FROM odin_knowledge_nodes ORDER BY timestamp DESC LIMIT ?"
            params = (limit,)
        async with self._db.execute(query, params) as cur:
            async for row in cur:
                out.append(_row_to_node(row))
        return out

    async def upsert_relationship(self, rel: dict[str, Any]) -> None:
        if not self._db:
            return
        await self._db.execute(
            "INSERT OR REPLACE INTO odin_knowledge_relationships VALUES (?,?,?,?,?,?)",
            (
                rel["id"],
                rel["source_entity"],
                rel["target_entity"],
                rel["relation"],
                rel.get("confidence", 0.5),
                rel.get("timestamp", datetime.now(timezone.utc).isoformat()),
            ),
        )
        await self._db.commit()

    async def list_relationships(self, *, limit: int = 50) -> list[dict[str, Any]]:
        if not self._db:
            return []
        out: list[dict] = []
        async with self._db.execute(
            "SELECT rel_id, source_entity, target_entity, relation, confidence, timestamp FROM odin_knowledge_relationships LIMIT ?",
            (limit,),
        ) as cur:
            async for row in cur:
                out.append(
                    {
                        "id": row[0],
                        "source_entity": row[1],
                        "target_entity": row[2],
                        "relation": row[3],
                        "confidence": row[4],
                        "timestamp": row[5],
                    }
                )
        return out

    async def save_source(self, source: dict[str, Any]) -> None:
        if not self._db:
            return
        await self._db.execute(
            "INSERT OR REPLACE INTO odin_knowledge_sources VALUES (?,?,?,?,?)",
            (source["id"], source["url"], source.get("title", ""), source.get("trust_score", 0.5), source["fetched_at"]),
        )
        await self._db.commit()

    async def list_sources(self, *, limit: int = 50) -> list[dict[str, Any]]:
        if not self._db:
            return []
        out: list[dict] = []
        async with self._db.execute(
            "SELECT source_id, url, title, trust_score, fetched_at FROM odin_knowledge_sources ORDER BY fetched_at DESC LIMIT ?",
            (limit,),
        ) as cur:
            async for row in cur:
                out.append(
                    {"id": row[0], "url": row[1], "title": row[2], "trust_score": row[3], "fetched_at": row[4]}
                )
        return out


def _row_to_node(row: tuple) -> dict[str, Any]:
    return {
        "id": row[0],
        "entity": row[1],
        "fact": row[2],
        "confidence": row[3],
        "source": row[4],
        "timestamp": row[5],
        "supporting_evidence": json.loads(row[6] or "[]"),
        "contradicting_evidence": json.loads(row[7] or "[]"),
        "mission_origin": row[8],
        "reasoning_chain": json.loads(row[9] or "[]"),
        "metadata": json.loads(row[10] or "{}"),
    }
