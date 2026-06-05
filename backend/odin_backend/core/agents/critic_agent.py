"""Critic cognitive agent."""

from __future__ import annotations

from typing import Any

from odin_backend.core.agents.base_agent import AgentReasoningStep, CognitiveAgent


class CriticAgent(CognitiveAgent):
    kind = "critic"

    async def run(self, *, objective: str, mission_id: str | None = None, context: dict[str, Any] | None = None) -> AgentReasoningStep:
        plan = (context or {}).get("plan", objective)
        prompt = f"Critique this plan for risks and contradictions:\n{plan}"
        text, model = await self._infer(prompt, task_kind="reflection", mission_id=mission_id)
        return AgentReasoningStep(agent_kind=self.kind, content=text, model=model, confidence=0.65)
