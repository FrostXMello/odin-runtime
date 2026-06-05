"""Base agent — specialize, execute, report. Never couple agents directly."""

from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from odin_backend.agents.protocols import ToolExecutorProtocol
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId, Task, TaskResult
from odin_backend.events.bus import EventBus
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class AgentState(StrEnum):
    IDLE = "idle"
    LISTENING = "listening"
    EXECUTING = "executing"
    WAITING = "waiting"
    BUSY = "executing"  # alias
    ERROR = "error"
    OFFLINE = "offline"


class AgentCapabilities(BaseModel):
    """Declared agent capabilities for orchestrator routing."""

    domains: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    can_delegate: bool = False
    max_concurrent_tasks: int = 1


class Agent(ABC):
    """
    Abstract specialized agent.

    Agents execute tasks and report via events — they do not call each other directly.
    """

    agent_id: AgentId
    display_name: str
    description: str
    capabilities: AgentCapabilities

    def __init__(self, event_bus: EventBus, tool_executor: ToolExecutorProtocol) -> None:
        self._event_bus = event_bus
        self._tool_executor = tool_executor
        self._state = AgentState.IDLE
        self._current_task_id: str | None = None

    @property
    def state(self) -> AgentState:
        return self._state

    @property
    def is_available(self) -> bool:
        return self._state == AgentState.IDLE

    async def on_register(self) -> None:
        await self._event_bus.publish(
            Event(
                type=EventType.AGENT_REGISTERED,
                source=self.agent_id,
                payload={"agent": self.agent_id, "capabilities": self.capabilities.model_dump()},
            )
        )

    async def heartbeat(self) -> None:
        await self._event_bus.publish(
            Event(
                type=EventType.AGENT_HEARTBEAT,
                source=self.agent_id,
                payload={"state": self._state, "current_task": self._current_task_id},
            )
        )

    async def handle_task(self, task: Task) -> TaskResult:
        """Entry point — wraps execution with lifecycle events."""
        self._state = AgentState.BUSY
        self._current_task_id = task.id
        task.mark_running(self.agent_id)

        await self._event_bus.publish(
            Event(
                type=EventType.TASK_STARTED,
                source=self.agent_id,
                task_id=task.id,
                correlation_id=task.parent_task_id,
                payload={"title": task.title},
            )
        )

        try:
            result = await self.execute(task)
            await self._event_bus.publish(
                Event(
                    type=EventType.TASK_COMPLETED,
                    source=self.agent_id,
                    task_id=task.id,
                    payload=result.model_dump(),
                )
            )
            return result
        except Exception as exc:
            logger.exception("agent_task_failed", agent=self.agent_id, task_id=task.id)
            await self._event_bus.publish(
                Event(
                    type=EventType.AGENT_FAILED,
                    source=self.agent_id,
                    task_id=task.id,
                    payload={"error": str(exc)},
                )
            )
            return TaskResult(success=False, error=str(exc))
        finally:
            self._state = AgentState.IDLE
            self._current_task_id = None

    @abstractmethod
    async def execute(self, task: Task) -> TaskResult:
        """Agent-specific task execution logic."""

    def can_handle(self, task: Task) -> bool:
        """Whether this agent accepts the task (override for routing)."""
        if task.assigned_agent and task.assigned_agent != self.agent_id:
            return False
        if task.required_tools:
            return all(t in self.capabilities.tools for t in task.required_tools)
        return True

    def get_info(self) -> dict[str, Any]:
        return {
            "id": self.agent_id,
            "name": self.display_name,
            "description": self.description,
            "state": self._state,
            "capabilities": self.capabilities.model_dump(),
        }
