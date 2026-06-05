"""Orphan queue and execution cleanup."""

from __future__ import annotations

from typing import Any


async def cleanup_orphans(app: Any) -> dict[str, Any]:
    cleaned: list[str] = []
    queue = getattr(app, "distributed_queue", None) or getattr(app, "task_queue", None)
    if queue and hasattr(queue, "list_orphaned"):
        orphans = await queue.list_orphaned()
        for item in orphans:
            if hasattr(queue, "ack_orphan"):
                await queue.ack_orphan(item.get("id", ""))
            cleaned.append(str(item.get("id", "unknown")))
    exec_store = getattr(app, "_sqlite_execution_store", None)
    if exec_store and hasattr(exec_store, "list_stale"):
        stale = await exec_store.list_stale(max_age_s=3600)
        cleaned.extend([s.get("execution_id", "") for s in stale if s.get("execution_id")])
    return {"cleaned": len(cleaned), "ids": cleaned[:20]}
