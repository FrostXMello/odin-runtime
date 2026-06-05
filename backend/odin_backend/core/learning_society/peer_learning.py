"""Peer learning engine."""

from __future__ import annotations

from typing import Any

from odin_backend.core.learning_society.expertise_transfer import transfer
from odin_backend.core.learning_society.mentor_selection import select_mentor
from odin_backend.core.learning_society.reasoning_pattern_library import ReasoningPatternLibrary
from odin_backend.core.learning_society.strategy_distillation import distill


class PeerLearningEngine:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._patterns = ReasoningPatternLibrary()

    async def teach(self, *, mentee_id: str, domain: str) -> dict[str, Any]:
        agents = await self._app.agent_society.list_agents()
        mentor = select_mentor(agents, domain=domain)
        if not mentor:
            return {"transferred": False, "reason": "no_mentor"}
        mentee = await self._app.agent_society.get_agent(mentee_id)
        if not mentee:
            return {"transferred": False, "reason": "mentee_not_found"}
        new_conf = transfer(
            mentor_confidence=float(mentor.get("confidence", 0.5)),
            mentee_confidence=float(mentee.get("confidence", 0.5)),
        )
        await self._app.agent_society.record_outcome(mentee_id, domain=domain, success=True)
        self._emit("agent_reflection_generated", {"mentee_id": mentee_id, "mentor_id": mentor.get("agent_id")})
        return {"transferred": True, "mentor": mentor.get("agent_id"), "new_confidence": new_conf}

    def distill_strategy(self, strategy: dict[str, Any]) -> dict[str, Any]:
        d = distill(strategy)
        self._patterns.add(name=d["name"], steps=d["steps"], source_agent=strategy.get("agent_id", "unknown"))
        return d

    def patterns(self) -> list[dict[str, Any]]:
        return self._patterns.list_patterns()

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="learning_society")
