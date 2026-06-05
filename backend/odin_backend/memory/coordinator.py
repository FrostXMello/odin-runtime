"""MIMIR — centralized memory coordination. All memory flows through here."""

from typing import Any

from odin_backend.core.bus.publish import publish_internal
from odin_backend.events.bus import EventBus
from odin_backend.memory.episodic.store import EpisodicStore
from odin_backend.memory.clusters import MemoryProject, infer_project
from odin_backend.memory.retrieval.engine import RetrievalEngine
from odin_backend.memory.scoring import MemoryScorer
from odin_backend.memory.semantic.store import SemanticStore
from odin_backend.memory.structured.store import StructuredStore
from odin_backend.memory.summarization import MemorySummarizer
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class MimirCoordinator:
    """Single entry point for episodic, structured, and semantic memory."""

    def __init__(self, event_bus: EventBus, settings: Any, *, observability: Any | None = None) -> None:
        self._event_bus = event_bus
        self._observability = observability
        self.episodic = EpisodicStore()
        self.structured = StructuredStore(settings)
        self.semantic = SemanticStore(settings)
        self.retrieval = RetrievalEngine(self.semantic, self.episodic)
        self.scorer = MemoryScorer()
        self.summarizer = MemorySummarizer()
        self._active_project: MemoryProject = MemoryProject.PROJECT_ODIN

    async def startup(self) -> None:
        await self.structured.connect()
        await self.semantic.connect()

    async def shutdown(self) -> None:
        await self.structured.disconnect()
        await self.semantic.disconnect()

    async def save_memory(
        self,
        content: str,
        *,
        category: str = "general",
        metadata: dict[str, Any] | None = None,
        session_id: str | None = None,
        project: str | None = None,
    ) -> str:
        meta = dict(metadata or {})
        proj = project or meta.get("project") or infer_project(content, meta).value
        meta["project"] = proj
        memory_id = await self.semantic.store(content, category=category, metadata=meta)
        await self.episodic.record(
            "memory.saved",
            {"memory_id": memory_id, "category": category},
            session_id=session_id,
        )
        if self._observability:
            from odin_backend.core.observability.events import TraceEventKind

            rec = self._observability.memory_audit.record(
                actor=meta.get("actor", "mimir"),
                reason=meta.get("reason", "save_memory"),
                category=category,
                memory_id=memory_id,
                new_value=content[:500],
                mission_id=meta.get("mission_id"),
                task_id=meta.get("task_id"),
                metadata=meta,
            )
            self._observability.tracer.record(
                TraceEventKind.MEMORY_MUTATED,
                message="semantic store",
                payload={"memory_id": memory_id, "mutation_id": rec.mutation_id},
                component="mimir",
            )
            self._observability.metrics.record_memory_mutation(category=category)
        await self._emit(EventType.MEMORY_UPDATED, {"memory_id": memory_id, "category": category})
        return memory_id

    async def search_memory(
        self, query: str, limit: int = 5, *, project: str | None = None
    ) -> list[dict[str, Any]]:
        results = await self.retrieval.search(query, limit=limit * 2)
        active = project or self._active_project.value
        for r in results:
            mid = r.get("id", "")
            if mid:
                self.scorer.record_access(str(mid))
                r["score"] = self.scorer.score(
                    str(mid),
                    project=r.get("metadata", {}).get("project"),
                    active_project=active,
                ).model_dump()
        if project:
            results = [r for r in results if r.get("metadata", {}).get("project") == project]
        results = sorted(results, key=lambda x: x.get("score", {}).get("score", 0), reverse=True)
        await self._emit(EventType.MEMORY_RETRIEVED, {"query": query, "count": len(results[:limit])})
        return results[:limit]

    async def retrieve_related_context(self, query: str, limit: int = 3, *, project: str | None = None) -> str:
        results = await self.search_memory(query, limit=limit, project=project)
        if not results:
            return ""
        return "\n".join(r.get("content", "") for r in results)

    def set_active_project(self, project: MemoryProject | str) -> None:
        self._active_project = MemoryProject(project) if isinstance(project, str) else project

    async def list_clusters(self) -> list[dict[str, Any]]:
        from odin_backend.memory.clusters import PROJECT_KEYWORDS

        return [
            {"project": p.value, "keywords": PROJECT_KEYWORDS.get(p, [])}
            for p in MemoryProject
        ]

    async def summarize_project(self, project: str) -> dict:
        results = await self.search_memory(project, limit=20, project=project)
        texts = [r.get("content", "") for r in results]
        summary = await self.summarizer.summarize_project(project, texts)
        return summary.model_dump(mode="json")

    async def record_workflow(self, workflow_id: str, event: str, payload: dict) -> None:
        await self.episodic.record(event, payload, workflow_id=workflow_id)
        await self.structured.log_workflow_event(workflow_id, event, payload)

    async def get_preference(self, key: str, default: Any = None) -> Any:
        return await self.structured.get_preference(key, default)

    async def set_preference(self, key: str, value: Any) -> None:
        await self.structured.set_preference(key, value)
        await self._emit(EventType.MEMORY_UPDATED, {"key": key, "tier": "structured"})

    async def _emit(self, event_type: EventType, payload: dict) -> None:
        await publish_internal(
            self._event_bus,
            Event(type=event_type, source=AgentId.MIMIR, payload=payload),
        )
