"""Unified retrieval across semantic + episodic."""

from typing import Any

from odin_backend.memory.episodic.store import EpisodicStore
from odin_backend.memory.semantic.store import SemanticStore


class RetrievalEngine:
    def __init__(self, semantic: SemanticStore, episodic: EpisodicStore) -> None:
        self._semantic = semantic
        self._episodic = episodic

    async def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        semantic_results = await self._semantic.search(query, limit=limit)
        recent = await self._episodic.query(limit=3)
        episodic_hits = [
            {
                "id": e.id,
                "content": f"{e.event}: {e.payload}",
                "metadata": {"source": "episodic", "workflow_id": e.workflow_id},
            }
            for e in recent
            if query.lower() in str(e.payload).lower()
        ]
        combined = semantic_results + episodic_hits
        return combined[:limit]
