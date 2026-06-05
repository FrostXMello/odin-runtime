"""Production vector memory runtime."""

from __future__ import annotations

from typing import Any

from odin_backend.core.vector_memory.embedding_runtime import embed_chunks
from odin_backend.core.vector_memory.episodic_memory import EpisodicMemory
from odin_backend.core.vector_memory.long_term_memory import LongTermMemory
from odin_backend.core.vector_memory.retrieval_pipeline import retrieve
from odin_backend.core.vector_memory.semantic_cache import SemanticCache


class VectorMemoryRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._cache = SemanticCache()
        self._episodic = EpisodicMemory()
        self._long_term = LongTermMemory()

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

    def record_episode(self, *, event: str, context: dict) -> dict[str, Any]:
        return self._episodic.record(event=event, context=context)

    def snapshot(self) -> dict[str, Any]:
        embed_metrics = {}
        if hasattr(self._app, "embedding_runtime"):
            embed_metrics = self._app.embedding_runtime.metrics
        return {
            "cache_size": self._cache.size(),
            "episodes": len(self._episodic._episodes),
            "long_term": len(self._long_term._entries),
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
