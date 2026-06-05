"""Runtime health checks and recovery signals."""

from odin_backend.events.bus import EventBus
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId
from odin_backend.runtime.registry.agent_registry import AgentRuntimeRegistry
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class HealthChecker:
    def __init__(
        self,
        event_bus: EventBus,
        runtime_registry: AgentRuntimeRegistry,
        stale_threshold_seconds: int = 45,
    ) -> None:
        self._event_bus = event_bus
        self._runtime = runtime_registry
        self._stale_threshold = stale_threshold_seconds

    async def check(self) -> dict:
        stale = self._runtime.get_stale(self._stale_threshold)
        for agent_id in stale:
            self._runtime.mark_unhealthy(agent_id)
            await self._event_bus.publish(
                Event(
                    type=EventType.RUNTIME_SERVICE_FAILED,
                    source=AgentId.HEIMDALL,
                    payload={"agent": str(agent_id), "reason": "heartbeat_stale"},
                )
            )
            logger.warning("agent_stale", agent_id=str(agent_id))

        healthy_count = sum(1 for r in self._runtime.list_all() if r.health == "healthy")
        return {
            "healthy_agents": healthy_count,
            "stale_agents": [str(a) for a in stale],
            "total": len(self._runtime.list_all()),
        }
