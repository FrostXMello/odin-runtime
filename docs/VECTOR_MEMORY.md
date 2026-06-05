# Vector Memory Runtime (v0.34)

Odin’s memory layer now uses real local embeddings and vector retrieval while preserving existing runtime APIs.

## Modules

- `core/vector_memory/embedding_runtime.py` — bridge to configured local embedding runtime.
- `core/vector_memory/vector_runtime.py` — orchestrator mounted as `app.vector_memory`.
- `core/vector_memory/chunking.py` — deterministic chunk segmentation.
- `core/vector_memory/retrieval_pipeline.py` — context-window-aware retrieval flow.
- `core/vector_memory/reranking.py` — reranks candidates by relevance + importance.
- `core/vector_memory/semantic_cache.py` — semantic deduplication cache.
- `core/vector_memory/episodic_memory.py` — short-horizon replay memory.
- `core/vector_memory/long_term_memory.py` — persistent scored memory entries.

## Storage model

- Default persistence: SQLite.
- Retrieval is local-only.
- API boundaries are kept compatible for future FAISS/Chroma adapters.

## Behavior

- Generates embeddings locally for each chunk.
- Persists chunk metadata and importance scores.
- Retrieves by semantic similarity with token-budget awareness.
- Applies reranking before final context assembly.
- Supports episodic replay and long-term memory promotion.
- Deduplicates near-identical memory fragments before index growth.
