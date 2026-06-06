"""Advanced memory intelligence (Prompt 51)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.memory_intelligence.contextual_recall_runtime import recall
from odin_backend.core.memory_intelligence.episodic_compression_runtime import compress
from odin_backend.core.memory_intelligence.long_horizon_memory_planner import plan
from odin_backend.core.memory_intelligence.predictive_memory_runtime import PredictiveMemoryRuntime
from odin_backend.core.memory_intelligence.semantic_relationship_engine import relate


class MemoryIntelligenceRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._predictive = PredictiveMemoryRuntime(app)

    async def map_relationships(self, *, a: str, b: str) -> dict[str, Any]:
        if not getattr(self._app.settings, "memory_intelligence_enabled", False):
            return {"accepted": False, "reason": "memory_intelligence_disabled"}
        rel = relate(a=a, b=b)
        if hasattr(self._app, "memory_fabric_v2"):
            await self._app.memory_fabric_v2.link_semantic(topic=a, prior=b)
        return {"accepted": True, "relationship": rel}

    async def recall_contextual(self, *, query: str) -> dict[str, Any]:
        r = await recall(self._app, query=query)
        return {"accepted": True, "recall": r}

    async def predict_resurface(self, *, topic: str) -> dict[str, Any]:
        return await self._predictive.resurface(topic=topic)

    async def compress_episodes(self, *, count: int = 10) -> dict[str, Any]:
        c = compress(episodes=count)
        return {"accepted": True, "compression": c}

    async def plan_horizon(self, *, days: int = 30) -> dict[str, Any]:
        p = plan(days=days)
        return {"accepted": True, "plan": p}

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
        obs.tracer.record(kind, message=kind_name, payload=payload, component="memory_intelligence")
