"""Agent communication protocol — all traffic flows through ODIN."""

from typing import Any

from odin_backend.core.bus.signals import Signal
from odin_backend.core.bus.unified_bus import SignalUnificationBus
from odin_backend.core.kernel.kernel import OdinCognitiveKernel
from odin_backend.events.bus import EventBus
from odin_backend.models.agent_message import AgentMessage, AgentMessageType
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId, TaskCreate
from odin_backend.models.task_graph import TaskNode, TaskNodeStatus
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class AgentProtocolHub:
    """
    Enforces: Agent → ODIN only; ODIN → Agent assignment.
    No peer-to-peer agent messaging.
    """

    def __init__(self, event_bus: EventBus, kernel: OdinCognitiveKernel) -> None:
        self._event_bus = event_bus
        self._kernel = kernel

    async def receive_from_agent(self, message: AgentMessage) -> dict[str, Any]:
        """Inbound agent report — normalized to Signal → kernel."""
        if not message.to_odin:
            raise ValueError("Agent messages must target ODIN")

        signal = Signal.from_agent_message(message)
        await self._kernel.process_signal(signal)

        if message.task_id:
            status = TaskNodeStatus.COMPLETE
            if message.type == AgentMessageType.ERROR:
                status = TaskNodeStatus.FAILED
            elif message.type == AgentMessageType.UPDATE:
                status = TaskNodeStatus.RUNNING
            self._kernel.task_graph.update_status(
                message.task_id,
                status,
                output=message.payload,
            )

        event = Event(
            type=EventType.AGENT_MESSAGE_RECEIVED,
            source=message.from_agent,
            task_id=message.task_id or None,
            payload={
                "message_id": message.id,
                "type": message.type.value,
                "confidence": message.confidence,
                "requires_escalation": message.requires_escalation,
                **message.payload,
            },
        )
        await self._publish(event)

        if message.requires_escalation:
            await self._publish(
                Event(
                    type=EventType.SECURITY_ESCALATION,
                    source=AgentId.ODIN,
                    task_id=message.task_id or None,
                    payload={"reason": "agent_requires_escalation", "from": message.from_agent},
                )
            )

        return {"accepted": True, "signal_id": signal.id, "task_id": message.task_id}

    async def assign_task(
        self,
        *,
        goal: str,
        agent_id: str,
        task_id: str | None = None,
        dependencies: list[str] | None = None,
        priority: int = 50,
        payload: dict | None = None,
    ) -> TaskNode:
        """ODIN → agent task assignment via task graph node."""
        from uuid import uuid4

        node = TaskNode(
            id=task_id or str(uuid4()),
            goal=goal,
            dependencies=dependencies or [],
            assigned_agent=agent_id,
            status=TaskNodeStatus.PENDING,
            priority=priority,
            output=payload or {},
        )
        self._kernel.task_graph.add_node(node)

        await self._publish(
            Event(
                type=EventType.TASK_CREATED,
                source=AgentId.ODIN,
                task_id=node.id,
                payload={
                    "goal": goal,
                    "assigned_agent": agent_id,
                    "assignment": "odin_to_agent",
                },
            )
        )
        await self._publish(
            Event(
                type=EventType.TASK_GRAPH_UPDATED,
                source=AgentId.ODIN,
                payload=self._kernel.task_graph.snapshot(),
            )
        )
        return node

    async def submit_orchestrator_task(self, orchestrator: Any, create: TaskCreate) -> Any:
        """Create orchestrator task and mirror node in kernel task graph."""
        routed = orchestrator._route_task(create)
        task = await orchestrator._task_queue.create(routed)
        priority_map = {"low": 30, "normal": 50, "high": 70, "critical": 90}
        pr = create.priority.value if hasattr(create.priority, "value") else str(create.priority)
        node = TaskNode(
            id=task.id,
            goal=create.description or create.title,
            assigned_agent=str(create.assigned_agent) if create.assigned_agent else None,
            status=TaskNodeStatus.PENDING,
            priority=priority_map.get(pr, 50),
            input_signals=[],
        )
        self._kernel.task_graph.add_node(node)
        return task

    async def _publish(self, event: Event) -> None:
        if isinstance(self._event_bus, SignalUnificationBus):
            await self._event_bus.inner.publish(event)
        else:
            await self._event_bus.publish(event)
