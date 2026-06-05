"""Agent heartbeat emission loop."""

import asyncio
from typing import Callable, Awaitable

from odin_backend.agents.registry import AgentRegistry
from odin_backend.core.bus.publish import publish_internal
from odin_backend.events.bus import EventBus
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId
from odin_backend.runtime.registry.agent_registry import AgentRuntimeRegistry
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class HeartbeatMonitor:
    def __init__(
        self,
        event_bus: EventBus,
        runtime_registry: AgentRuntimeRegistry,
        agent_registry: AgentRegistry,
        interval_seconds: int = 15,
    ) -> None:
        self._event_bus = event_bus
        self._runtime = runtime_registry
        self._agents = agent_registry
        self._interval = interval_seconds
        self._task: asyncio.Task | None = None
        self._running = False

    async def start(self) -> None:
        self._running = True
        self._task = asyncio.create_task(self._loop())
        logger.info("heartbeat_monitor_started", interval=self._interval)

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _loop(self) -> None:
        while self._running:
            try:
                for info in self._agents.list_agents():
                    agent_id = AgentId(info["id"])
                    rec = self._runtime.heartbeat(agent_id, metrics={"source": "heartbeat_loop"})
                    await publish_internal(
                        self._event_bus,
                        Event(
                            type=EventType.AGENT_HEARTBEAT,
                            source=agent_id,
                            payload={
                                "state": rec.state,
                                "health": rec.health,
                                "active_workflows": rec.active_workflows,
                            },
                        )
                    )
                    await publish_internal(
                        self._event_bus,
                        Event(
                            type=EventType.RUNTIME_HEARTBEAT,
                            source=AgentId.ODIN,
                            payload={"agent": str(agent_id), "health": rec.health},
                        )
                    )
            except Exception as exc:
                logger.exception("heartbeat_loop_error", error=str(exc))
            await asyncio.sleep(self._interval)
