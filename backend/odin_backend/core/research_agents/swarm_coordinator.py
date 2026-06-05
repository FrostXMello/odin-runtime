"""Coordinate parallel research agents."""

from __future__ import annotations

import asyncio
from typing import Any

from odin_backend.core.research_agents.agents import (
    CriticAgent,
    HistorianAgent,
    ScoutAgent,
    StrategistAgent,
    SynthesizerAgent,
    VerifierAgent,
)


class ResearchSwarmCoordinator:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._agents = [
            ScoutAgent(),
            VerifierAgent(),
            CriticAgent(),
            SynthesizerAgent(),
            HistorianAgent(),
            StrategistAgent(),
        ]

    async def investigate(self, *, topic: str, evidence: list[dict]) -> dict[str, Any]:
        results = await asyncio.gather(*[a.run(self._app, topic=topic, evidence=evidence) for a in self._agents])
        consensus = sum(1 for r in results if r.get("role") == "verifier" and r.get("verified_count", 0) > 0)
        if hasattr(self._app, "reasoning_world"):
            self._app.reasoning_world.record_hypothesis(topic=topic, hypothesis=f"Consensus on {topic}", confidence=0.6)
            self._emit("hypothesis_generated", {"topic": topic})
        return {"agents": results, "consensus": consensus / max(len(self._agents), 1)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="research_swarm")
