"""In-memory knowledge graph operations."""

from __future__ import annotations

from typing import Any

from odin_backend.core.knowledge.knowledge_relationships import KnowledgeRelationship
from odin_backend.core.knowledge.semantic_entities import extract_entities


class KnowledgeGraph:
    def __init__(self) -> None:
        self._adjacency: dict[str, set[str]] = {}

    def link(self, *, source: str, target: str, relation: str, confidence: float = 0.5) -> KnowledgeRelationship:
        self._adjacency.setdefault(source, set()).add(target)
        self._adjacency.setdefault(target, set()).add(source)
        return KnowledgeRelationship(
            source_entity=source, target_entity=target, relation=relation, confidence=confidence
        )

    def neighbors(self, entity: str) -> list[str]:
        return sorted(self._adjacency.get(entity, set()))

    def infer_relationships(self, text: str) -> list[KnowledgeRelationship]:
        entities = extract_entities(text)
        rels: list[KnowledgeRelationship] = []
        for i, a in enumerate(entities):
            for b in entities[i + 1 :]:
                rels.append(self.link(source=a, target=b, relation="co_mentioned", confidence=0.4))
        return rels

    def snapshot(self) -> dict[str, Any]:
        return {"nodes": list(self._adjacency.keys()), "edge_count": sum(len(v) for v in self._adjacency.values()) // 2}
