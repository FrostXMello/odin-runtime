"""Persistent memory fabric V2 (Prompt 50)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.memory_fabric_v2.context_rehydration_engine import ContextRehydrationEngine
from odin_backend.core.memory_fabric_v2.cross_session_linker import link
from odin_backend.core.memory_fabric_v2.episodic_replay_runtime import replay
from odin_backend.core.memory_fabric_v2.knowledge_compression_runtime import compress
from odin_backend.core.memory_fabric_v2.memory_decay_manager import prune


class PersistentSemanticMemory:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._rehydration = ContextRehydrationEngine(app)
        self._links: list[dict] = []

    async def link_semantic(self, *, topic: str, prior: str) -> dict[str, Any]:
        if not getattr(self._app.settings, "memory_fabric_v2_enabled", False):
            return {"accepted": False, "reason": "memory_fabric_v2_disabled"}
        l = link(topic=topic, prior=prior)
        self._links.append(l)
        self._emit("semantic_memory_linked", l)
        if hasattr(self._app, "memory_fabric"):
            await self._app.memory_fabric.link(topic=topic, prior=prior)
        return {"accepted": True, "link": l}

    async def compress_history(self, *, tokens: int = 4096) -> dict[str, Any]:
        c = compress(tokens=tokens)
        return {"accepted": True, "compression": c}

    async def replay_session(self, *, session: str) -> dict[str, Any]:
        r = replay(session=session)
        return {"accepted": True, "replay": r}

    async def rehydrate_context(self, *, session: str) -> dict[str, Any]:
        return await self._rehydration.rehydrate(session=session)

    async def prune_memory(self, *, age_days: int = 45) -> dict[str, Any]:
        p = prune(age_days=age_days)
        return {"accepted": True, "prune": p}

    def snapshot(self) -> dict[str, Any]:
        return {"links": len(self._links)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="memory_fabric_v2")
