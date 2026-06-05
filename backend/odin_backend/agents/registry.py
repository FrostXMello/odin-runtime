"""Agent registry — discover and route to specialized agents."""

from odin_backend.agents.base import Agent
from odin_backend.models.task import AgentId, Task
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class AgentRegistry:
    """Central catalog of registered agents."""

    def __init__(self) -> None:
        self._agents: dict[AgentId, Agent] = {}

    def register(self, agent: Agent) -> None:
        self._agents[agent.agent_id] = agent
        logger.info("agent_registered", agent_id=agent.agent_id)

    def get(self, agent_id: AgentId) -> Agent | None:
        return self._agents.get(agent_id)

    def list_agents(self) -> list[dict]:
        return [agent.get_info() for agent in self._agents.values()]

    def find_handler(self, task: Task) -> Agent | None:
        if task.assigned_agent:
            agent = self.get(task.assigned_agent)
            if agent and agent.can_handle(task) and agent.is_available:
                return agent
            return None

        for agent in self._agents.values():
            if agent.agent_id == AgentId.ODIN:
                continue
            if agent.is_available and agent.can_handle(task):
                return agent
        return None

    async def register_all(self) -> None:
        for agent in self._agents.values():
            await agent.on_register()
