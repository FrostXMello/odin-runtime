"""Semantic retrieval for planner context."""

from __future__ import annotations

from typing import Any

from odin_backend.core.memory.context.embeddings import rank_by_similarity
from odin_backend.core.memory.context.semantic_memory import SemanticMemoryEntry


class PlannerRetriever:
    def __init__(self) -> None:
        self._entries: list[SemanticMemoryEntry] = []

    def index(self, entry: SemanticMemoryEntry) -> None:
        self._entries.append(entry)
        if len(self._entries) > 500:
            self._entries = self._entries[-500:]

    def retrieve(self, query: str, *, mission_id: str | None = None, limit: int = 5) -> list[dict[str, Any]]:
        items = [
            (e.entry_id, e.text)
            for e in self._entries
            if mission_id is None or e.mission_id == mission_id or e.mission_id is None
        ]
        ranked = rank_by_similarity(query, items, limit=limit)
        id_set = {k for k, _ in ranked}
        out: list[dict[str, Any]] = []
        for e in self._entries:
            if e.entry_id in id_set:
                score = next(s for k, s in ranked if k == e.entry_id)
                out.append({"entry_id": e.entry_id, "text": e.text, "kind": e.kind, "score": score, "metadata": e.metadata})
        return sorted(out, key=lambda x: -x["score"])
