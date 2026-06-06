"""Storage optimization orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.storage_optimization.archive_runtime import archive_entries
from odin_backend.core.storage_optimization.cold_storage import ColdStorage
from odin_backend.core.storage_optimization.embedding_cache import EmbeddingCache
from odin_backend.core.storage_optimization.retrieval_acceleration import accelerate
from odin_backend.core.storage_optimization.archival_policy import apply_archival
from odin_backend.core.storage_optimization.storage_analytics import analyze_storage


class StorageOptimizationRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._cache = EmbeddingCache()
        self._cold = ColdStorage()

    async def optimize(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "storage_optimization_enabled", False):
            return {"accepted": False, "reason": "storage_optimization_disabled"}
        compacted = 0
        if hasattr(self._app, "vector_memory"):
            result = await self._app.vector_memory.compact()
            compacted += result.get("evicted", 0)
        accel = accelerate("global", cache_hits=self._cache.size(), total=max(self._cache.size(), 1))
        self._emit("retrieval_optimized", accel)
        return {"accepted": True, "cache_size": self._cache.size(), "compacted": compacted, "acceleration": accel}

    async def archive(self, entries: list[dict[str, Any]]) -> dict[str, Any]:
        result = archive_entries(entries)
        for _ in range(result["archived"]):
            self._cold.store({"archived": True})
        return {"accepted": True, **result}

    async def analytics(self) -> dict[str, Any]:
        projects = 0
        if hasattr(self._app, "project_os"):
            projects = len(self._app.project_os._registry.list_all())
        return analyze_storage(
            cache_size=self._cache.size(),
            cold_size=self._cold.count(),
            projects=projects,
        )

    async def apply_retention(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "storage_optimization_enabled", False):
            return {"accepted": False, "reason": "storage_optimization_disabled"}
        stats = await self.analytics()
        policy = apply_archival(cache_entries=stats["cache_entries"])
        return {"accepted": True, "analytics": stats, "policy": policy}

    def snapshot(self) -> dict[str, Any]:
        return {"cache_size": self._cache.size(), "cold_storage": self._cold.count()}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="storage_optimization")
