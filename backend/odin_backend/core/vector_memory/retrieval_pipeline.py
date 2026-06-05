"""Context-window aware retrieval pipeline."""

from __future__ import annotations

from typing import Any

from odin_backend.core.vector_memory.reranking import rerank_results


async def retrieve(app: Any, query: str, *, limit: int = 5, max_context_tokens: int = 4096) -> list[dict[str, Any]]:
    results: list[dict] = []
    if hasattr(app, "embedding_runtime"):
        results = await app.embedding_runtime.hybrid_search(query, limit=limit)
    elif hasattr(app, "vector_memory"):
        results = await app.vector_memory.search(query, limit=limit)
    reranked = rerank_results(query, results)
    budget = max_context_tokens * 4
    out = []
    used = 0
    for item in reranked:
        text = str(item.get("label", item.get("content", "")))
        if used + len(text) > budget:
            break
        out.append(item)
        used += len(text)
    return out
