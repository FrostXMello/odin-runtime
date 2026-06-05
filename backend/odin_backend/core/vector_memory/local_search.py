"""Local semantic search."""

from __future__ import annotations

from typing import Any


async def hybrid_search(app: Any, query: str, *, limit: int = 10) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    if hasattr(app, "vector_memory"):
        vm_hits = await app.vector_memory.search(query, limit=limit)
        results.extend([{"source": "vector_memory", **h} if isinstance(h, dict) else {"source": "vector_memory", "text": str(h)} for h in vm_hits])
    if hasattr(app, "workspace_knowledge"):
        ws_hits = await app.workspace_knowledge.search(query, limit=limit)
        results.extend([{"source": "workspace", **h} for h in ws_hits])
    if hasattr(app, "project_os"):
        for p in app.project_os._registry.list_all():
            if query.lower() in p.get("name", "").lower():
                results.append({"source": "project", "project": p})
    return {"query": query, "results": results[:limit], "count": len(results[:limit])}
