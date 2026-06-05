"""Synthesizer cognitive agent."""

from __future__ import annotations

from typing import Any

from odin_backend.core.agents.base_agent import AgentReasoningStep, CognitiveAgent


class SynthesizerAgent(CognitiveAgent):
    kind = "synthesizer"

    async def run(self, *, objective: str, mission_id: str | None = None, context: dict[str, Any] | None = None) -> AgentReasoningStep:
        steps = (context or {}).get("steps", [])
        joined = "\n".join(f"- {s.get('content', s)}" for s in steps) if steps else objective
        prompt = f"Synthesize a coherent execution strategy from:\n{joined}"
        text, model = await self._infer(prompt, task_kind="synthesis", mission_id=mission_id)
        return AgentReasoningStep(agent_kind=self.kind, content=text, model=model, confidence=0.78)
