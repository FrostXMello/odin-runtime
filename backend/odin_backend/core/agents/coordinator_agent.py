"""Coordinate cognitive agents with reflection guards."""

from __future__ import annotations

from typing import Any

from odin_backend.core.agents.base_agent import AgentReasoningStep
from odin_backend.core.agents.critic_agent import CriticAgent
from odin_backend.core.agents.memory_agent import MemoryAgent
from odin_backend.core.agents.planner_agent import PlannerAgent
from odin_backend.core.agents.researcher_agent import ResearcherAgent
from odin_backend.core.agents.synthesizer_agent import SynthesizerAgent
from odin_backend.core.agents.verifier_agent import VerifierAgent


class CognitiveAgentCoordinator:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._agents = {
            "planner": PlannerAgent(app),
            "researcher": ResearcherAgent(app),
            "critic": CriticAgent(app),
            "verifier": VerifierAgent(app),
            "memory": MemoryAgent(app),
            "synthesizer": SynthesizerAgent(app),
        }
        self._chains: dict[str, list[dict[str, Any]]] = {}

    def list_agents(self) -> list[str]:
        return list(self._agents.keys())

    async def run_pipeline(
        self,
        *,
        objective: str,
        mission_id: str | None = None,
        max_depth: int | None = None,
    ) -> dict[str, Any]:
        depth_limit = max_depth or getattr(self._app.settings, "reflection_max_depth", 2)
        steps: list[AgentReasoningStep] = []
        mem = await self._agents["memory"].run(objective=objective, mission_id=mission_id)
        steps.append(mem)
        research = await self._agents["researcher"].run(objective=objective, mission_id=mission_id)
        steps.append(research)
        plan = await self._agents["planner"].run(objective=objective, mission_id=mission_id)
        steps.append(plan)
        if depth_limit >= 1:
            critic = await self._agents["critic"].run(
                objective=objective, mission_id=mission_id, context={"plan": plan.content}
            )
            steps.append(critic)
        verify = await self._agents["verifier"].run(
            objective=objective, mission_id=mission_id, context={"plan": plan.content}
        )
        steps.append(verify)
        synth = await self._agents["synthesizer"].run(
            objective=objective,
            mission_id=mission_id,
            context={"steps": [s.model_dump() for s in steps]},
        )
        steps.append(synth)
        chain = [s.model_dump() for s in steps]
        if mission_id:
            self._chains[mission_id] = chain
        return {"objective": objective, "mission_id": mission_id, "steps": chain, "synthesis": synth.content}

    def get_chain(self, mission_id: str) -> list[dict[str, Any]]:
        return self._chains.get(mission_id, [])
