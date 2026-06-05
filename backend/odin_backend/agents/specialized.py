"""Specialized agents — execute via tool runtime, report via events."""

from odin_backend.agents.base import Agent, AgentCapabilities
from odin_backend.agents.execution import ToolExecutionMixin
from odin_backend.models.task import AgentId, Task, TaskResult
from odin_backend.agents.protocols import ToolExecutorProtocol
from odin_backend.events.bus import EventBus
from odin_backend.memory.coordinator import MimirCoordinator


class _ExecutionAgent(ToolExecutionMixin, Agent):
    async def execute(self, task: Task) -> TaskResult:
        return await self.execute_tools_for_task(task)


class ValkyrieAgent(_ExecutionAgent):
    agent_id = AgentId.VALKYRIE
    display_name = "Valkyrie"
    description = "Operations, desktop execution, workflow automation"
    capabilities = AgentCapabilities(
        domains=["automation", "desktop", "workflows"],
        tools=[
            "take_screenshot",
            "open_browser",
            "get_browser_tabs",
            "extract_tab_content",
            "list_directory",
            "read_file",
            "write_file",
        ],
    )


class MimirAgent(_ExecutionAgent):
    agent_id = AgentId.MIMIR
    display_name = "Mimir"
    description = "Memory, vector retrieval, semantic search"
    capabilities = AgentCapabilities(
        domains=["memory", "knowledge"],
        tools=["read_file", "write_file", "list_directory"],
    )

    def __init__(
        self,
        event_bus: EventBus,
        tool_executor: ToolExecutorProtocol,
        memory: MimirCoordinator,
    ) -> None:
        super().__init__(event_bus, tool_executor)
        self._memory = memory

    async def execute(self, task: Task) -> TaskResult:
        action = task.payload.get("memory_action")
        if action == "search":
            query = task.payload.get("query", task.title)
            results = await self._memory.search_memory(query)
            return TaskResult(success=True, output={"results": results})
        if action == "save":
            content = task.payload.get("content", task.description)
            mid = await self._memory.save_memory(content, category=task.payload.get("category", "general"))
            return TaskResult(success=True, output={"memory_id": mid})
        return await self.execute_tools_for_task(task)


class HuginAgent(_ExecutionAgent):
    agent_id = AgentId.HUGIN
    display_name = "Hugin"
    description = "Web research, monitoring, data gathering"
    capabilities = AgentCapabilities(
        domains=["research", "web"],
        tools=["search_web", "extract_tab_content"],
    )


class MuninAgent(_ExecutionAgent):
    agent_id = AgentId.MUNIN
    display_name = "Munin"
    description = "Summarization, analysis, report generation"
    capabilities = AgentCapabilities(
        domains=["analysis", "reports"],
        tools=["summarize_content"],
    )


class BrokkAgent(_ExecutionAgent):
    agent_id = AgentId.BROKK
    display_name = "Brokk"
    description = "Engineering, coding, debugging"
    capabilities = AgentCapabilities(
        domains=["engineering", "code"],
        tools=["read_file", "write_file", "execute_terminal"],
    )


class HeimdallAgent(_ExecutionAgent):
    agent_id = AgentId.HEIMDALL
    display_name = "Heimdall"
    description = "Security, monitoring, permissions"
    capabilities = AgentCapabilities(
        domains=["security", "monitoring"],
        tools=["get_system_info"],
    )


class BragiAgent(_ExecutionAgent):
    agent_id = AgentId.BRAGI
    display_name = "Bragi"
    description = "Writing, communication, creative generation"
    capabilities = AgentCapabilities(
        domains=["writing", "communication"],
        tools=["generate_email", "send_email"],
    )


def create_specialized_agents(
    event_bus: EventBus,
    tool_executor: ToolExecutorProtocol,
    memory: MimirCoordinator,
) -> list[Agent]:
    return [
        ValkyrieAgent(event_bus, tool_executor),
        MimirAgent(event_bus, tool_executor, memory),
        HuginAgent(event_bus, tool_executor),
        MuninAgent(event_bus, tool_executor),
        BrokkAgent(event_bus, tool_executor),
        HeimdallAgent(event_bus, tool_executor),
        BragiAgent(event_bus, tool_executor),
    ]
