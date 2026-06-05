"""Federated memory runtime."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import aiosqlite

from odin_backend.core.federated_memory.contradiction_resolution import resolve_contradiction
from odin_backend.core.federated_memory.knowledge_sharing import KnowledgeSharing
from odin_backend.core.federated_memory.memory_lineage import MemoryLineage
from odin_backend.core.federated_memory.memory_replication import MemoryReplication
from odin_backend.core.federated_memory.semantic_exchange import exchange_embedding
from odin_backend.core.federated_memory.trust_weighting import weight_by_trust

_SCHEMA = """
CREATE TABLE IF NOT EXISTS odin_federated_memory (
    memory_id TEXT PRIMARY KEY,
    from_node TEXT NOT NULL,
    content_json TEXT NOT NULL,
    trust REAL NOT NULL DEFAULT 0.5,
    version INTEGER NOT NULL DEFAULT 1,
    lineage TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL
);
"""


class FederatedMemoryRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._path = app.settings.database_url.replace("sqlite+aiosqlite:///", "")
        self._db: aiosqlite.Connection | None = None
        self._sharing = KnowledgeSharing()
        self._replication = MemoryReplication()
        self._lineage = MemoryLineage()

    async def connect(self) -> None:
        self._db = await aiosqlite.connect(self._path)
        await self._db.executescript(_SCHEMA)
        await self._db.commit()

    async def disconnect(self) -> None:
        if self._db:
            await self._db.close()
            self._db = None

    async def share(self, *, from_node: str, fact: str, confidence: float, trust: float = 0.5) -> dict[str, Any]:
        if not getattr(self._app.settings, "federation_enabled", False):
            return {"accepted": False, "reason": "federation_disabled"}
        fed = getattr(self._app, "federation_runtime", None)
        mode = fed.snapshot().get("mode", "isolated") if fed else "isolated"
        local_only = mode == "isolated" and getattr(self._app.settings, "federation_enabled", False)
        if fed and not local_only and not fed._policies.allow_knowledge_share(mode, trust):
            return {"accepted": False, "reason": "trust_too_low"}
        if trust < getattr(self._app.settings, "federation_min_trust_share", 0.4):
            return {"accepted": False, "reason": "trust_too_low"}
        lineage_id = str(uuid4())
        self._lineage.record(lineage_id, source=from_node)
        entry = self._sharing.share(from_node=from_node, fact=fact, confidence=confidence, lineage=lineage_id)
        weighted = weight_by_trust(value=confidence, trust=trust)
        embedding = exchange_embedding(content=fact, trust=trust)
        if self._db:
            now = datetime.now(timezone.utc).isoformat()
            await self._db.execute(
                "INSERT OR REPLACE INTO odin_federated_memory VALUES (?,?,?,?,?,?,?)",
                (entry["id"], from_node, json.dumps({"fact": fact, "embedding": embedding}), trust, 1, json.dumps([from_node]), now),
            )
            await self._db.commit()
        if hasattr(self._app, "knowledge_runtime"):
            await self._app.knowledge_runtime.ingest_fact(
                entity=f"federation:{from_node}", fact=fact, confidence=weighted, source="federated_memory"
            )
        self._emit("knowledge_shared", {"from_node": from_node, "fact": fact[:80], "trust": trust})
        return {"accepted": True, "share": entry, "weighted_confidence": weighted}

    async def list_memories(self, limit: int = 50) -> list[dict[str, Any]]:
        if not self._db:
            return []
        out = []
        async with self._db.execute(
            "SELECT memory_id, from_node, content_json, trust, version, lineage FROM odin_federated_memory LIMIT ?",
            (limit,),
        ) as cur:
            async for row in cur:
                out.append({
                    "memory_id": row[0], "from_node": row[1],
                    "content": json.loads(row[2]), "trust": row[3],
                    "version": row[4], "lineage": json.loads(row[5]),
                })
        return out

    def resolve(self, a: dict, b: dict) -> dict[str, Any]:
        return resolve_contradiction(a, b)

    def snapshot(self) -> dict[str, Any]:
        return {
            "shares": len(self._sharing.list_all()),
            "replicas": len(self._replication.list_all()),
        }

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="federated_memory")
