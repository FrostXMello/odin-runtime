"""Knowledge fabric runtime orchestrator."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from odin_backend.core.knowledge.belief_state import BeliefState
from odin_backend.core.knowledge.confidence_decay import decay_confidence, is_stale
from odin_backend.core.knowledge.contradiction_engine import detect_contradictions
from odin_backend.core.knowledge.knowledge_graph import KnowledgeGraph
from odin_backend.core.knowledge.knowledge_nodes import KnowledgeNode
from odin_backend.core.knowledge.knowledge_store import KnowledgeStore
from odin_backend.core.knowledge.semantic_entities import extract_entities
from odin_backend.core.knowledge.temporal_knowledge import TemporalKnowledge
from odin_backend.core.knowledge.world_model import WorldModel


class KnowledgeRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._store = KnowledgeStore(app.settings)
        self._graph = KnowledgeGraph()
        self._beliefs = BeliefState()
        self._temporal = TemporalKnowledge()
        self._world = WorldModel()
        self._enabled = getattr(app.settings, "knowledge_fabric_enabled", False)

    async def connect(self) -> None:
        await self._store.connect()

    async def disconnect(self) -> None:
        await self._store.disconnect()

    async def ingest_fact(
        self,
        *,
        entity: str,
        fact: str,
        confidence: float = 0.6,
        source: str = "local",
        mission_origin: str | None = None,
        evidence: list[str] | None = None,
    ) -> dict[str, Any]:
        if not self._enabled:
            return {"accepted": False, "reason": "knowledge_fabric_disabled"}
        node = KnowledgeNode(
            entity=entity,
            fact=fact,
            confidence=confidence,
            source=source,
            mission_origin=mission_origin,
            supporting_evidence=evidence or [],
        )
        data = node.model_dump(mode="json")
        await self._store.upsert_node(data)
        self._beliefs.update(entity, fact=fact, confidence=confidence, source=source)
        self._temporal.record(entity=entity, fact=fact, confidence=confidence)
        self._world.apply_fact(entity=entity, fact=fact, confidence=confidence)
        for rel in self._graph.infer_relationships(fact):
            await self._store.upsert_relationship(rel.model_dump(mode="json"))
        self._emit("knowledge_created", {"entity": entity, "node_id": node.id})
        self._emit("belief_updated", {"entity": entity, "confidence": confidence})
        self._emit("world_model_updated", {"entity_count": self._world.snapshot()["entity_count"]})
        if hasattr(self._app, "cognitive_memory"):
            from odin_backend.core.cognition.entities import MemoryEntity, MemoryEntityKind

            await self._app.cognitive_memory.upsert_entity(
                MemoryEntity(
                    kind=MemoryEntityKind.SEMANTIC,
                    label=entity,
                    confidence=confidence,
                    mission_id=mission_origin,
                    metadata={"fact": fact, "source": source},
                )
            )
        return data

    async def list_knowledge(self, *, entity: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        return await self._store.list_nodes(limit=limit, entity=entity)

    async def contradictions(self) -> list[dict[str, Any]]:
        nodes = await self._store.list_nodes(limit=200)
        found = detect_contradictions(nodes)
        for c in found:
            self._emit("contradiction_detected", c)
        return found

    async def decay_stale(self) -> list[dict[str, Any]]:
        stale_items: list[dict] = []
        nodes = await self._store.list_nodes(limit=200)
        for n in nodes:
            try:
                ts = datetime.fromisoformat(str(n["timestamp"]).replace("Z", "+00:00"))
            except Exception:
                continue
            if is_stale(updated_at=ts):
                decayed = decay_confidence(confidence=n["confidence"], age_days=(datetime.now(timezone.utc) - ts).days)
                n["confidence"] = decayed
                await self._store.upsert_node(n)
                stale_items.append(n)
                self._emit("stale_knowledge_detected", {"entity": n["entity"], "confidence": decayed})
        return stale_items

    def snapshot(self) -> dict[str, Any]:
        return {
            "enabled": self._enabled,
            "graph": self._graph.snapshot(),
            "beliefs": self._beliefs.snapshot()[-20:],
            "world_model": self._world.snapshot(),
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
        obs.tracer.record(kind, message=kind_name, payload=payload, component="knowledge_runtime")
