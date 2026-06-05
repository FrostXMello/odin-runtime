"""Memory retrieval — similarity, success lookup, failure patterns."""

from __future__ import annotations

from typing import Any

from odin_backend.core.cognition.entities import MemoryEntityKind
from odin_backend.core.cognition.memory_graph import CognitiveMemoryGraph


class RetrievalEngine:
    def __init__(self, graph: CognitiveMemoryGraph) -> None:
        self._graph = graph

    async def similar_executions(self, query: str, *, limit: int = 5) -> list[dict[str, Any]]:
        hits = self._graph.search_similar(query, limit=limit * 2)
        out: list[dict[str, Any]] = []
        if not self._graph._db:
            return out
        for eid, score in hits:
            async with self._graph._db.execute(
                "SELECT entity_id, label, confidence, mission_id, metadata FROM odin_cognition_entities WHERE entity_id=? AND kind=?",
                (eid, MemoryEntityKind.EPISODIC.value),
            ) as cur:
                row = await cur.fetchone()
            if row:
                out.append(
                    {
                        "entity_id": row[0],
                        "label": row[1],
                        "confidence": row[2],
                        "mission_id": row[3],
                        "score": score,
                        "metadata": row[4],
                    }
                )
            if len(out) >= limit:
                break
        return out

    async def nearest_successful(self, query: str, *, limit: int = 3) -> list[dict[str, Any]]:
        similar = await self.similar_executions(query, limit=limit * 3)
        return [s for s in similar if s.get("confidence", 0) >= 0.6][:limit]

    async def recall_strategy(self, domain: str) -> list[dict[str, Any]]:
        if not self._graph._db:
            return []
        out: list[dict] = []
        async with self._graph._db.execute(
            """SELECT label, confidence, metadata FROM odin_cognition_entities
               WHERE kind=? AND label LIKE ? ORDER BY confidence DESC LIMIT 5""",
            (MemoryEntityKind.PROCEDURAL.value, f"%{domain}%"),
        ) as cur:
            async for row in cur:
                out.append({"label": row[0], "confidence": row[1], "metadata": row[2]})
        return out

    async def failure_patterns(self, *, limit: int = 10) -> list[dict[str, Any]]:
        if not self._graph._db:
            return []
        out: list[dict] = []
        async with self._graph._db.execute(
            """SELECT label, confidence, mission_id, metadata FROM odin_cognition_entities
               WHERE kind=? AND confidence < 0.45 ORDER BY updated_at DESC LIMIT ?""",
            (MemoryEntityKind.EPISODIC.value, limit),
        ) as cur:
            async for row in cur:
                out.append(
                    {
                        "label": row[0],
                        "confidence": row[1],
                        "mission_id": row[2],
                        "metadata": row[3],
                    }
                )
        return out
