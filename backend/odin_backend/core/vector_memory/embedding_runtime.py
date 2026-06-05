"""Vector memory embedding bridge."""

from __future__ import annotations

from typing import Any

from odin_backend.core.vector_memory.chunking import chunk_with_importance


async def embed_chunks(app: Any, text: str, *, metadata: dict | None = None) -> list[str]:
    chunks = chunk_with_importance(text)
    ids = []
    for chunk in chunks:
        if hasattr(app, "embedding_runtime"):
            chunk_ids = await app.embedding_runtime.embed_and_index(
                chunk["text"], metadata={**(metadata or {}), "importance": chunk["importance"]}
            )
            ids.extend(chunk_ids)
    return ids
