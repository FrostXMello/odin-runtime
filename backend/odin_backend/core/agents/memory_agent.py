"""Memory cognitive agent."""

from __future__ import annotations

from typing import Any

from odin_backend.core.agents.base_agent import AgentReasoningStep, CognitiveAgent


class MemoryAgent(CognitiveAgent):
    kind = "memory"

    async def run(self, *, objective: str, mission_id: str | None = None, context: dict[str, Any] | None = None) -> AgentReasoningStep:
        patterns = []
        if hasattr(self._app, "memory_retrieval"):
            patterns = await self._app.memory_retrieval.failure_patterns(limit=3)
            strategies = await self._app.memory_retrieval.recall_strategy("api")
        else:
            strategies = []
        summary = f"Failures: {patterns}\nStrategies: {strategies}"
        self._emit_trace("memory_grounded", {"patterns": len(patterns)}, mission_id=mission_id)
        return AgentReasoningStep(agent_kind=self.kind, content=summary, confidence=0.85, metadata={"patterns": patterns})
