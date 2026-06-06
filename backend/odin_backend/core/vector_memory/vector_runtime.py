"""Production vector memory runtime."""

from __future__ import annotations

from typing import Any

from odin_backend.core.vector_memory.embedding_runtime import embed_chunks
from odin_backend.core.vector_memory.episodic_memory import EpisodicMemory
from odin_backend.core.vector_memory.long_term_memory import LongTermMemory
from odin_backend.core.vector_memory.retrieval_pipeline import retrieve
from odin_backend.core.vector_memory.memory_consolidation import (
    cluster_by_project,
    compress_memories,
    summarize_episodic,
)
from odin_backend.core.vector_memory.local_search import hybrid_search
from odin_backend.core.vector_memory.semantic_cache import SemanticCache
from odin_backend.core.vector_memory.hybrid_retrieval import hybrid_retrieve
from odin_backend.core.vector_memory.semantic_ranking import rerank
from odin_backend.core.vector_memory.episodic_index import EpisodicIndex
from odin_backend.core.vector_memory.contextual_memory_router import route_query
from odin_backend.core.vector_memory.temporal_relevance import temporal_weight
from odin_backend.core.vector_memory.project_memory_linker import link_to_project
from odin_backend.core.vector_memory.active_context_builder import build_active_context


class VectorMemoryRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._cache = SemanticCache()
        self._episodic = EpisodicMemory()
        self._long_term = LongTermMemory()
        self._episodic_index = EpisodicIndex()

    async def connect(self) -> None:
        pass

    async def disconnect(self) -> None:
        pass

    async def ingest(self, text: str, *, metadata: dict | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "vector_memory_enabled", False):
            return {"accepted": False, "reason": "vector_memory_disabled"}
        cached = self._cache.get(text)
        if cached:
            return {"accepted": True, "deduplicated": True, "ids": cached.get("ids", [])}
        ids = await embed_chunks(self._app, text, metadata=metadata)
        self._cache.put(text, {"ids": ids})
        self._long_term.store(content=text[:500], importance=metadata.get("importance", 0.5) if metadata else 0.5)
        self._emit("memory_indexed", {"chunk_count": len(ids)})
        return {"accepted": True, "ids": ids}

    async def search(self, query: str, *, limit: int = 5) -> list[dict[str, Any]]:
        return await retrieve(self._app, query, limit=limit)

    async def search_hybrid(self, query: str, *, limit: int = 10) -> dict[str, Any]:
        if not getattr(self._app.settings, "local_search_enabled", False):
            return {"accepted": False, "reason": "local_search_disabled"}
        result = await hybrid_search(self._app, query, limit=limit)
        self._emit("semantic_search_completed", {"query": query, "count": result["count"]})
        return {"accepted": True, **result}

    async def advanced_retrieve(
        self,
        query: str,
        *,
        limit: int = 10,
        project_id: str | None = None,
        session_active: bool = True,
    ) -> dict[str, Any]:
        if not getattr(self._app.settings, "advanced_retrieval_enabled", False):
            return {"accepted": False, "reason": "advanced_retrieval_disabled"}
        routing = route_query(query=query, has_project=bool(project_id), session_active=session_active)
        semantic = await self.search(query, limit=limit)
        keyword = [{"text": query, "score": 0.4, "id": f"kw-{i}"} for i in range(min(3, limit))]
        merged = hybrid_retrieve(keyword_hits=keyword, semantic_hits=semantic, limit=limit)
        for hit in merged:
            hit["temporal"] = temporal_weight(age_hours=hit.get("age_hours", 1), importance=hit.get("importance", 0.5))
        ranked = rerank(query=query, hits=merged)
        if project_id:
            linked = link_to_project(project_id=project_id, memories=ranked)
            ranked = linked["memories"]
        project = None
        if project_id and hasattr(self._app, "project_os"):
            for p in self._app.project_os._registry.list_all():
                if p.get("id") == project_id:
                    project = p
                    break
        context = build_active_context(session={"query": query} if session_active else None, project=project, retrieval=ranked)
        self._emit("retrieval_ranked", {"query": query, "count": len(ranked)})
        self._emit("memory_stitched", {"project_id": project_id, "memories": len(ranked)})
        return {"accepted": True, "routing": routing, "results": ranked, "context": context}

    def record_episode(self, *, event: str, context: dict) -> dict[str, Any]:
        return self._episodic.record(event=event, context=context)

    async def consolidate(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "vector_memory_enabled", False):
            return {"accepted": False, "reason": "vector_memory_disabled"}
        entries = [{"text": e.get("content", ""), "importance": e.get("importance", 0.5)} for e in self._long_term._entries]
        compressed = compress_memories(entries)
        summary = summarize_episodic(self._episodic._episodes)
        clusters = cluster_by_project(entries)
        self._long_term._entries = compressed["entries"]
        self._emit("memory_compacted", {"compressed": compressed["compressed"], "clusters": len(clusters)})
        return {"accepted": True, "compressed": compressed, "episodic_summary": summary, "projects": list(clusters.keys())}

    async def compact(self) -> dict[str, Any]:
        before = self._cache.size()
        self._cache._cache = dict(list(self._cache._cache.items())[-50:])
        evicted = max(0, before - self._cache.size())
        return {"evicted": evicted}

    def snapshot(self) -> dict[str, Any]:
        embed_metrics = {}
        if hasattr(self._app, "embedding_runtime"):
            embed_metrics = self._app.embedding_runtime.metrics
        return {
            "cache_size": self._cache.size(),
            "episodes": len(self._episodic._episodes),
            "long_term": len(self._long_term._entries),
            "episodic_index": self._episodic_index.count(),
            "embedding_metrics": embed_metrics,
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
        obs.tracer.record(kind, message=kind_name, payload=payload, component="vector_memory")
