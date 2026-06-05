"""Planner cognitive agent."""

from __future__ import annotations

from typing import Any

from odin_backend.core.agents.base_agent import AgentReasoningStep, CognitiveAgent


class PlannerAgent(CognitiveAgent):
    kind = "planner"

    async def run(self, *, objective: str, mission_id: str | None = None, context: dict[str, Any] | None = None) -> AgentReasoningStep:
        grounding = ""
        if hasattr(self._app, "reasoning_pipeline"):
            ctx = await self._app.reasoning_pipeline.build(objective=objective, mission_id=mission_id)
            grounding = ctx.get("prompt_block", "")
        prompt = f"Plan steps for objective:\n{objective}\n\nMemory context:\n{grounding}"
        text, model = await self._infer(prompt, task_kind="planning", mission_id=mission_id)
        step = AgentReasoningStep(agent_kind=self.kind, content=text, model=model, confidence=0.75)
        self._emit_trace("reasoning_chain_extended", step.model_dump(), mission_id=mission_id)
        return step
