"""Cognitive memory graph — persistent entities and relationships."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import aiosqlite

from odin_backend.config import Settings
from odin_backend.core.cognition.decay import decay_confidence
from odin_backend.core.cognition.entities import MemoryEntity, MemoryEntityKind
from odin_backend.core.cognition.relationships import MemoryRelationship, RelationshipType
from odin_backend.core.cognition.vector_index import VectorIndex
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS odin_cognition_entities (
    entity_id TEXT PRIMARY KEY,
    kind TEXT NOT NULL,
    label TEXT NOT NULL,
    confidence REAL NOT NULL DEFAULT 0.5,
    reinforcement REAL NOT NULL DEFAULT 0,
    mission_id TEXT,
    task_id TEXT,
    execution_id TEXT,
    metadata TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS odin_cognition_relationships (
    relationship_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    rel_type TEXT NOT NULL,
    weight REAL NOT NULL DEFAULT 0.5,
    metadata TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_cog_entity_mission ON odin_cognition_entities(mission_id);
CREATE INDEX IF NOT EXISTS idx_cog_entity_kind ON odin_cognition_entities(kind);
CREATE INDEX IF NOT EXISTS idx_cog_rel_source ON odin_cognition_relationships(source_id);
"""


class CognitiveMemoryGraph:
    def __init__(self, settings: Settings, app: Any | None = None) -> None:
        self._app = app
        self._db_path = settings.database_url.replace("sqlite+aiosqlite:///", "")
        self._db: aiosqlite.Connection | None = None
        self._index = VectorIndex()
        self._metrics: dict[str, int] = {"entities": 0, "relationships": 0, "reinforced": 0}

    async def connect(self) -> None:
        self._db = await aiosqlite.connect(self._db_path)
        await self._db.executescript(_SCHEMA)
        await self._db.commit()
        async with self._db.execute("SELECT entity_id, label FROM odin_cognition_entities") as cur:
            async for row in cur:
                self._index.upsert(row[0], row[1])
        logger.info("cognitive_memory_graph_connected")

    async def disconnect(self) -> None:
        if self._db:
            await self._db.close()
            self._db = None

    @property
    def metrics(self) -> dict[str, int]:
        return dict(self._metrics)

    async def upsert_entity(self, entity: MemoryEntity) -> MemoryEntity:
        conn = self._db
        if not conn:
            return entity
        await conn.execute(
            """INSERT INTO odin_cognition_entities
               (entity_id, kind, label, confidence, reinforcement, mission_id, task_id,
                execution_id, metadata, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(entity_id) DO UPDATE SET
                 label=excluded.label,
                 confidence=excluded.confidence,
                 reinforcement=excluded.reinforcement,
                 metadata=excluded.metadata,
                 updated_at=excluded.updated_at""",
            (
                entity.entity_id,
                entity.kind.value,
                entity.label,
                entity.confidence,
                entity.reinforcement,
                entity.mission_id,
                entity.task_id,
                entity.execution_id,
                json.dumps(entity.metadata),
                entity.created_at.isoformat(),
                entity.updated_at.isoformat(),
            ),
        )
        await conn.commit()
        self._index.upsert(entity.entity_id, entity.label)
        self._metrics["entities"] += 1
        return entity

    async def add_relationship(self, rel: MemoryRelationship) -> MemoryRelationship:
        if not self._db:
            return rel
        await self._db.execute(
            """INSERT INTO odin_cognition_relationships
               (relationship_id, source_id, target_id, rel_type, weight, metadata, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                rel.relationship_id,
                rel.source_id,
                rel.target_id,
                rel.rel_type.value,
                rel.weight,
                json.dumps(rel.metadata),
                rel.created_at.isoformat(),
            ),
        )
        await self._db.commit()
        self._metrics["relationships"] += 1
        return rel

    async def reinforce(self, entity_id: str, *, success: bool, amount: float = 0.1) -> None:
        if not self._db:
            return
        delta = amount if success else -amount * 0.5
        conf_delta = 0.05 if success else -0.08
        await self._db.execute(
            """UPDATE odin_cognition_entities
               SET reinforcement=reinforcement+?,
                   confidence=MIN(0.99, MAX(0.05, confidence+?)),
                   updated_at=?
               WHERE entity_id=?""",
            (delta, conf_delta, datetime.now(timezone.utc).isoformat(), entity_id),
        )
        await self._db.commit()
        self._metrics["reinforced"] += 1
        if success:
            from odin_backend.core.observability.events import TraceEventKind

            obs = getattr(self._app, "observability", None) if self._app else None
            if obs:
                obs.tracer.record(
                    TraceEventKind.MEMORY_REINFORCED,
                    message="memory reinforced",
                    payload={"entity_id": entity_id, "delta": delta},
                    component="cognitive_memory",
                )

    async def link_execution(
        self,
        *,
        mission_id: str,
        task_id: str | None,
        execution_id: str,
        summary: str,
        success: bool,
        capability: str | None = None,
        tool: str | None = None,
    ) -> str:
        from odin_backend.core.cognition.episodic_memory import episodic_from_execution

        entity = episodic_from_execution(
            mission_id=mission_id,
            task_id=task_id,
            execution_id=execution_id,
            summary=summary,
            success=success,
            metadata={"capability": capability, "tool": tool},
        )
        await self.upsert_entity(entity)
        if capability:
            cap_ent = MemoryEntity(
                kind=MemoryEntityKind.CAPABILITY,
                label=capability,
                mission_id=mission_id,
                confidence=0.7 if success else 0.4,
            )
            await self.upsert_entity(cap_ent)
            await self.add_relationship(
                MemoryRelationship(
                    source_id=entity.entity_id,
                    target_id=cap_ent.entity_id,
                    rel_type=RelationshipType.SOLVED_BY if success else RelationshipType.CAUSED_FAILURE,
                    weight=0.8 if success else 0.3,
                )
            )
        return entity.entity_id

    async def decay_stale(self, *, max_age_days: float = 30.0) -> int:
        if not self._db:
            return 0
        cutoff = datetime.now(timezone.utc).timestamp() - max_age_days * 86400
        count = 0
        async with self._db.execute("SELECT entity_id, confidence, updated_at FROM odin_cognition_entities") as cur:
            async for row in cur:
                updated = datetime.fromisoformat(row[2].replace("Z", "+00:00"))
                age = datetime.now(timezone.utc).timestamp() - updated.timestamp()
                new_conf = decay_confidence(float(row[1]), age_seconds=age)
                if new_conf < float(row[1]) - 0.01:
                    await self._db.execute(
                        "UPDATE odin_cognition_entities SET confidence=? WHERE entity_id=?",
                        (new_conf, row[0]),
                    )
                    count += 1
        await self._db.commit()
        return count

    async def export_snapshot(self, *, limit: int = 100) -> dict[str, Any]:
        if not self._db:
            return {"entities": [], "relationships": []}
        entities: list[dict] = []
        async with self._db.execute(
            "SELECT entity_id, kind, label, confidence, mission_id FROM odin_cognition_entities ORDER BY updated_at DESC LIMIT ?",
            (limit,),
        ) as cur:
            async for row in cur:
                entities.append(
                    {
                        "entity_id": row[0],
                        "kind": row[1],
                        "label": row[2],
                        "confidence": row[3],
                        "mission_id": row[4],
                    }
                )
        rels: list[dict] = []
        async with self._db.execute(
            "SELECT source_id, target_id, rel_type, weight FROM odin_cognition_relationships LIMIT ?",
            (limit,),
        ) as cur:
            async for row in cur:
                rels.append(
                    {"source": row[0], "target": row[1], "type": row[2], "weight": row[3]}
                )
        return {"entities": entities, "relationships": rels, "metrics": self.metrics}

    def search_similar(self, query: str, *, limit: int = 10) -> list[tuple[str, float]]:
        return self._index.search(query, limit=limit)
