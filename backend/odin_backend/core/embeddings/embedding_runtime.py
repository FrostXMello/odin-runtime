"""Local embedding generation and hybrid retrieval."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from odin_backend.core.embeddings.chunking import chunk_text
from odin_backend.core.embeddings.reranking import rerank
from odin_backend.core.embeddings.semantic_index import SemanticIndex
from odin_backend.core.embeddings.vector_store import VectorStore


class EmbeddingRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._store = VectorStore(app.settings)
        self._index = SemanticIndex()
        self._metrics: dict[str, int] = {"embedded": 0, "searches": 0}

    async def connect(self) -> None:
        await self._store.connect()
        for row in await self._store.list_recent(limit=500):
            self._index.add(row)

    async def disconnect(self) -> None:
        await self._store.disconnect()

    @property
    def metrics(self) -> dict[str, int]:
        return dict(self._metrics)

    async def embed_and_index(self, text: str, *, metadata: dict[str, Any] | None = None) -> list[str]:
        model = self._app.settings.embedding_model
        ids: list[str] = []
        for chunk in chunk_text(text):
            vectors = await self._app.model_manager.runtime.embed([chunk], model=model)
            vid = str(uuid4())
            entry = {"vector_id": vid, "label": chunk[:200], "embedding": vectors[0], "metadata": metadata or {}}
            await self._store.upsert(vid, entry["label"], vectors[0], metadata)
            self._index.add(entry)
            ids.append(vid)
            self._metrics["embedded"] += 1
        return ids

    async def hybrid_search(self, query: str, *, limit: int = 5) -> list[dict[str, Any]]:
        self._metrics["searches"] += 1
        model = self._app.settings.embedding_model
        q_vec = (await self._app.model_manager.runtime.embed([query], model=model))[0]
        semantic = self._index.search(q_vec, limit=limit * 2)
        symbolic: list[dict] = []
        retrieval = getattr(self._app, "memory_retrieval", None)
        if retrieval:
            symbolic = await retrieval.similar_executions(query, limit=limit)
        merged = {h.get("vector_id") or h.get("entity_id") or h.get("label"): h for h in semantic}
        for s in symbolic:
            key = s.get("entity_id") or s.get("label")
            merged[key] = {**s, "source": "graph"}
        items = list(merged.values())[: limit * 2]
        if items and len(items) <= 20:
            docs = [str(i.get("label", "")) for i in items]
            try:
                scores = await self._app.model_manager.registry.provider.rerank(
                    model=model, query=query, documents=docs
                )
                items = rerank(query, items, scores)
            except Exception:
                pass
        return items[:limit]

    def snapshot(self) -> dict[str, Any]:
        return {"metrics": self.metrics, "index_size": len(self._index._entries)}
