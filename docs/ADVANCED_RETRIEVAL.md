# Advanced Retrieval

Odin v0.38 extends vector memory with project-aware hybrid retrieval.

## Capabilities

- Hybrid keyword + embedding merge
- Semantic reranking
- Temporal relevance weighting
- Active session context boosting
- Project memory linking
- Mission-context stitching

## API

- `GET /api/v1/runtime/retrieval`
- `POST /api/v1/runtime/retrieval/advanced`

```json
{ "query": "odin daemon restart", "limit": 10, "project_id": "proj-1" }
```

Trace kinds: `retrieval_ranked`, `memory_stitched` on `retrieval:runtime`.
