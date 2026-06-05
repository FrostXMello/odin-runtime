"""Researcher cognitive agent."""

from __future__ import annotations

from typing import Any

from odin_backend.core.agents.base_agent import AgentReasoningStep, CognitiveAgent


class ResearcherAgent(CognitiveAgent):
    kind = "researcher"

    async def run(self, *, objective: str, mission_id: str | None = None, context: dict[str, Any] | None = None) -> AgentReasoningStep:
        similar = []
        if hasattr(self._app, "memory_retrieval"):
            similar = await self._app.memory_retrieval.similar_executions(objective, limit=3)
        prompt = f"Research gaps for:\n{objective}\n\nSimilar executions:\n{similar}"
        text, model = await self._infer(prompt, task_kind="planning", mission_id=mission_id)
        return AgentReasoningStep(agent_kind=self.kind, content=text, model=model, confidence=0.7)
