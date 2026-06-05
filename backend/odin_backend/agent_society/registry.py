"""Agent capability registry and dynamic specialization routing."""

from typing import Any

from pydantic import BaseModel, Field

from odin_backend.agents.registry import AgentRegistry
from odin_backend.models.task import AgentId
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)

DOMAIN_AGENTS: dict[str, AgentId] = {
    "coding": AgentId.BROKK,
    "research": AgentId.HUGIN,
    "analysis": AgentId.MUNIN,
    "communication": AgentId.BRAGI,
    "security": AgentId.HEIMDALL,
    "memory": AgentId.MIMIR,
    "operations": AgentId.VALKYRIE,
}


class AgentCapabilityProfile(BaseModel):
    agent_id: str
    domains: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    reliability_score: float = 0.8
    collaboration_score: float = 0.8
    tasks_completed: int = 0
    tasks_failed: int = 0


class AgentSocietyRegistry:
    """ODIN uses this for routing — agents never self-coordinate."""

    def __init__(self, agent_registry: AgentRegistry) -> None:
        self._registry = agent_registry
        self._profiles: dict[str, AgentCapabilityProfile] = {}
        self._init_profiles()

    def _init_profiles(self) -> None:
        domain_map = {
            AgentId.HUGIN: ["research", "web"],
            AgentId.BROKK: ["coding", "technical"],
            AgentId.MUNIN: ["analysis", "synthesis"],
            AgentId.BRAGI: ["communication", "summarization"],
            AgentId.HEIMDALL: ["security"],
            AgentId.MIMIR: ["memory"],
            AgentId.VALKYRIE: ["operations"],
        }
        for agent in self._registry._agents.values():
            aid = str(agent.agent_id)
            self._profiles[aid] = AgentCapabilityProfile(
                agent_id=aid,
                domains=domain_map.get(agent.agent_id, ["general"]),
                tools=list(agent.capabilities.tools),
            )

    def record_task_outcome(self, agent_id: AgentId, success: bool) -> None:
        p = self._profiles.get(str(agent_id))
        if not p:
            return
        if success:
            p.tasks_completed += 1
            p.reliability_score = min(1.0, p.reliability_score + 0.01)
            p.collaboration_score = min(1.0, p.collaboration_score + 0.005)
        else:
            p.tasks_failed += 1
            p.reliability_score = max(0.1, p.reliability_score - 0.05)

    def route_task(self, domain: str, *, context: str = "") -> AgentId:
        """ODIN delegates — returns best agent for domain."""
        preferred = DOMAIN_AGENTS.get(domain, AgentId.VALKYRIE)
        candidates = [
            (aid, prof)
            for aid, prof in self._profiles.items()
            if domain in prof.domains or domain == "general"
        ]
        if not candidates:
            return preferred
        best = max(candidates, key=lambda x: x[1].reliability_score)
        return AgentId(best[0])

    def list_profiles(self) -> list[dict[str, Any]]:
        return [p.model_dump() for p in self._profiles.values()]

    def get_reputation(self, agent_id: str) -> dict[str, Any]:
        p = self._profiles.get(agent_id)
        if not p:
            return {}
        total = p.tasks_completed + p.tasks_failed
        return {
            "agent_id": agent_id,
            "reliability_score": p.reliability_score,
            "collaboration_score": p.collaboration_score,
            "completion_rate": p.tasks_completed / total if total else 1.0,
            "tasks_completed": p.tasks_completed,
            "domains": p.domains,
        }
