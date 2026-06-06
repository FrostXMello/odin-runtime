"""Cognitive maintenance (Prompt 53)."""
from __future__ import annotations
from typing import Any


class CognitiveMaintenanceRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app

    async def compact_memory_threads(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "cognitive_maintenance_enabled", False):
            return {"accepted": False, "reason": "cognitive_maintenance_disabled"}
        if hasattr(self._app, "memory_fabric_v2"):
            await self._app.memory_fabric_v2.compress_history(tokens=2048)
        self._emit("memory_threads_compacted", {"compacted": True})
        return {"accepted": True, "compacted": True}

    async def prune_inactive_contexts(self) -> dict[str, Any]:
        if hasattr(self._app, "memory_fabric_v2"):
            await self._app.memory_fabric_v2.prune_memory(age_days=45)
        return {"accepted": True, "pruned": True}

    async def compress_streams(self) -> dict[str, Any]:
        if hasattr(self._app, "cognitive_streams"):
            await self._app.cognitive_streams.reflect_stream(summary="overnight compaction")
        return {"accepted": True, "compressed": True}

    async def stabilize_runtime_state(self) -> dict[str, Any]:
        if hasattr(self._app, "runtime_coordination"):
            await self._app.runtime_coordination.resolve_priority_conflicts()
        self._emit("runtime_state_stabilized", {"stabilized": True})
        return {"accepted": True, "stabilized": True}

    def snapshot(self) -> dict[str, Any]:
        return {"enabled": True}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="cognitive_maintenance")
