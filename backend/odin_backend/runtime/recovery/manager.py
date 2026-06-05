"""Auto-recovery for stale runtime services."""

from odin_backend.agents.base import AgentState
from odin_backend.events.bus import EventBus
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId
from odin_backend.runtime.registry.agent_registry import AgentRuntimeRegistry
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class RecoveryManager:
    def __init__(self, event_bus: EventBus, runtime_registry: AgentRuntimeRegistry) -> None:
        self._event_bus = event_bus
        self._runtime = runtime_registry

    async def recover_agent(self, agent_id: AgentId) -> bool:
        rec = self._runtime.register(agent_id)
        rec.restart_count += 1
        rec.health = "healthy"
        rec.state = AgentState.IDLE
        await self._event_bus.publish(
            Event(
                type=EventType.RUNTIME_RECOVERY,
                source=AgentId.ODIN,
                payload={"agent": str(agent_id), "restart_count": rec.restart_count},
            )
        )
        logger.info("agent_recovered", agent_id=str(agent_id))
        return True
