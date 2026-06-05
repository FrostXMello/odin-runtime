"""ODIN — Central orchestrator. Does not execute all actions directly."""

import asyncio
from typing import Any

from odin_backend.agents.registry import AgentRegistry
from odin_backend.config import Settings
from odin_backend.events.bus import EventBus
from odin_backend.events.task_queue import TaskQueue
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId, Task, TaskCreate, TaskResult, TaskStatus
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


# Agent routing hints by task metadata domain
_DOMAIN_AGENT_MAP: dict[str, AgentId] = {
    "automation": AgentId.VALKYRIE,
    "desktop": AgentId.VALKYRIE,
    "memory": AgentId.MIMIR,
    "research": AgentId.HUGIN,
    "web": AgentId.HUGIN,
    "analysis": AgentId.MUNIN,
    "engineering": AgentId.BROKK,
    "code": AgentId.BROKK,
    "security": AgentId.HEIMDALL,
}


class OdinOrchestrator:
    """
    Central orchestrator.

    Responsibilities: plan, reason, delegate, monitor.
    Does NOT directly execute specialized work — delegates to agents.
    """

    def __init__(
        self,
        settings: Settings,
        event_bus: EventBus,
        task_queue: TaskQueue,
        agent_registry: AgentRegistry,
    ) -> None:
        self._settings = settings
        self._event_bus = event_bus
        self._task_queue = task_queue
        self._agents = agent_registry
        self._agent_protocol: Any = None
        self._worker_task: asyncio.Task[None] | None = None
        self._running = False
        self._active_tasks: dict[str, asyncio.Task[None]] = {}

    async def start(self) -> None:
        self._running = True
        await self._event_bus.publish(
            Event(type=EventType.SYSTEM_STARTED, source=AgentId.ODIN)
        )
        self._worker_task = asyncio.create_task(self._process_queue())
        logger.info("odin_orchestrator_started")

    async def stop(self) -> None:
        self._running = False
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        for task in self._active_tasks.values():
            task.cancel()
        await self._event_bus.publish(
            Event(type=EventType.SYSTEM_SHUTDOWN, source=AgentId.ODIN)
        )
        logger.info("odin_orchestrator_stopped")

    def set_agent_protocol(self, protocol: Any) -> None:
        self._agent_protocol = protocol

    async def submit_task(self, create: TaskCreate) -> Task:
        """Accept work, plan routing, enqueue for delegation."""
        if self._agent_protocol:
            return await self._agent_protocol.submit_orchestrator_task(self, create)
        routed = self._route_task(create)
        task = await self._task_queue.create(routed)
        logger.info(
            "odin_task_submitted",
            task_id=task.id,
            assigned=routed.assigned_agent,
        )
        return task

    async def get_task(self, task_id: str) -> Task | None:
        return await self._task_queue.get(task_id)

    async def cancel_task(self, task_id: str) -> Task | None:
        task = await self._task_queue.get(task_id)
        if not task:
            return None
        task.status = TaskStatus.CANCELLED
        await self._task_queue.update(task)
        await self._event_bus.publish(
            Event(
                type=EventType.TASK_CANCELLED,
                source=AgentId.ODIN,
                task_id=task_id,
            )
        )
        return task

    def _route_task(self, create: TaskCreate) -> TaskCreate:
        """Strategic routing — assign agent based on domain hints."""
        if create.assigned_agent:
            return create

        domain = create.metadata.get("domain") or create.payload.get("domain")
        if domain and domain in _DOMAIN_AGENT_MAP:
            return create.model_copy(update={"assigned_agent": _DOMAIN_AGENT_MAP[domain]})

        if create.required_tools:
            return create.model_copy(update={"assigned_agent": self._infer_agent(create)})

        return create

    def _infer_agent(self, create: TaskCreate) -> AgentId | None:
        tool_agent_hints: dict[str, AgentId] = {
            "search_web": AgentId.HUGIN,
            "execute_terminal": AgentId.BROKK,
            "take_screenshot": AgentId.VALKYRIE,
            "read_file": AgentId.MIMIR,
            "write_file": AgentId.MIMIR,
        }
        for tool in create.required_tools:
            if tool in tool_agent_hints:
                return tool_agent_hints[tool]
        return None

    async def _process_queue(self) -> None:
        while self._running:
            try:
                if len(self._active_tasks) >= self._settings.orchestrator_max_concurrent_tasks:
                    await asyncio.sleep(0.5)
                    continue

                task = await self._task_queue.dequeue()
                if task is None:
                    await asyncio.sleep(0.25)
                    continue

                worker = asyncio.create_task(self._delegate_task(task))
                self._active_tasks[task.id] = worker
                worker.add_done_callback(lambda t, tid=task.id: self._active_tasks.pop(tid, None))
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.exception("odin_queue_processor_error", error=str(exc))
                await asyncio.sleep(1)

    async def _delegate_task(self, task: Task) -> None:
        agent = self._agents.find_handler(task)
        if agent is None:
            task.mark_failed("No available agent to handle task")
            await self._task_queue.update(task)
            await self._event_bus.publish(
                Event(
                    type=EventType.TASK_FAILED,
                    source=AgentId.ODIN,
                    task_id=task.id,
                    payload={"error": task.error},
                )
            )
            return

        result = await agent.handle_task(task)
        if result.success:
            task.mark_completed(result)
        else:
            task.mark_failed(result.error or "Agent execution failed")
        await self._task_queue.update(task)

        if self._agent_protocol and task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
            from odin_backend.models.agent_message import AgentMessage, AgentMessageType

            await self._agent_protocol.receive_from_agent(
                AgentMessage(
                    from_agent=str(task.assigned_agent or AgentId.ODIN),
                    type=AgentMessageType.RESULT if result.success else AgentMessageType.ERROR,
                    payload=result.model_dump(),
                    task_id=task.id,
                    confidence=1.0 if result.success else 0.5,
                    requires_escalation=not result.success,
                )
            )

    async def get_system_status(self) -> dict[str, Any]:
        return {
            "orchestrator": "odin",
            "running": self._running,
            "active_tasks": len(self._active_tasks),
            "agents": self._agents.list_agents(),
        }
