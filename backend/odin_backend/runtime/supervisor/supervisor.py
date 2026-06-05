"""Runtime supervisor — persistent services, health, recovery."""

import asyncio
from typing import Any

from odin_backend.agents.registry import AgentRegistry
from odin_backend.config import Settings
from odin_backend.events.bus import EventBus
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId
from odin_backend.runtime.health.checker import HealthChecker
from odin_backend.runtime.heartbeat.monitor import HeartbeatMonitor
from odin_backend.runtime.lifecycle.hooks import LifecycleHooks
from odin_backend.runtime.recovery.manager import RecoveryManager
from odin_backend.runtime.registry.agent_registry import AgentRuntimeRegistry
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class RuntimeSupervisor:
    """Manages persistent ODIN runtime services."""

    def __init__(
        self,
        settings: Settings,
        event_bus: EventBus,
        agent_registry: AgentRegistry,
    ) -> None:
        self._settings = settings
        self._event_bus = event_bus
        self._agent_registry = agent_registry
        self.registry = AgentRuntimeRegistry()
        self.hooks = LifecycleHooks()
        self.heartbeat = HeartbeatMonitor(
            event_bus,
            self.registry,
            agent_registry,
            settings.runtime_heartbeat_interval_seconds,
        )
        self.health = HealthChecker(
            event_bus,
            self.registry,
            settings.runtime_health_check_interval_seconds,
        )
        self.recovery = RecoveryManager(event_bus, self.registry)
        self._health_task: asyncio.Task | None = None
        self._running = False
        self._services: dict[str, Any] = {}

    def register_service(self, name: str, service: Any) -> None:
        self._services[name] = service

    async def start(self) -> None:
        self._running = True
        for info in self._agent_registry.list_agents():
            self.registry.register(AgentId(info["id"]))

        await self.hooks.run_startup()
        await self.heartbeat.start()
        self._health_task = asyncio.create_task(self._health_loop())

        await self._event_bus.publish(
            Event(
                type=EventType.RUNTIME_SERVICE_STARTED,
                source=AgentId.ODIN,
                payload={"services": list(self._services.keys())},
            )
        )
        logger.info("runtime_supervisor_started")

    async def stop(self) -> None:
        self._running = False
        await self.heartbeat.stop()
        if self._health_task:
            self._health_task.cancel()
            try:
                await self._health_task
            except asyncio.CancelledError:
                pass
        await self.hooks.run_shutdown()
        logger.info("runtime_supervisor_stopped")

    async def _health_loop(self) -> None:
        while self._running:
            try:
                report = await self.health.check()
                for agent_str in report.get("stale_agents", []):
                    await self.recovery.recover_agent(AgentId(agent_str))
            except Exception as exc:
                logger.exception("health_loop_error", error=str(exc))
            await asyncio.sleep(self._settings.runtime_health_check_interval_seconds)

    def get_status(self) -> dict:
        return {
            "running": self._running,
            "agents": [r.model_dump(mode="json") for r in self.registry.list_all()],
            "services": list(self._services.keys()),
        }
