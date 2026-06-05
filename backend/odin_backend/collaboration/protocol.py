"""Collaboration protocol — all coordination through ODIN."""

from typing import Any

from odin_backend.agents.registry import AgentRegistry
from odin_backend.collaboration.payloads import CollaborationChain, SharedContextPayload
from odin_backend.events.bus import EventBus
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId, Task, TaskPriority
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)

# Predefined collaborative chains (ODIN supervises, does not auto-run dangerously)
COLLABORATION_TEMPLATES: dict[str, list[tuple[AgentId, str]]] = {
    "research_report": [
        (AgentId.HUGIN, "Gather data and sources"),
        (AgentId.BROKK, "Analyze technical architecture"),
        (AgentId.MUNIN, "Synthesize insights"),
        (AgentId.BRAGI, "Format final report"),
    ],
}


class CollaborationOrchestrator:
    """Coordinates multi-agent chains via ODIN task submission."""

    def __init__(self, event_bus: EventBus, agent_registry: AgentRegistry) -> None:
        self._event_bus = event_bus
        self._registry = agent_registry
        self._chains: dict[str, CollaborationChain] = {}

    def create_chain(self, template: str, objective: str) -> CollaborationChain | None:
        steps_def = COLLABORATION_TEMPLATES.get(template)
        if not steps_def:
            return None
        chain = CollaborationChain(
            objective=objective,
            steps=[
                {"agent": str(a), "description": desc} for a, desc in steps_def
            ],
        )
        self._chains[chain.id] = chain
        return chain

    async def request_assistance(
        self,
        chain_id: str,
        from_agent: AgentId,
        to_agent: AgentId,
        artifact: dict[str, Any],
        *,
        artifact_type: str = "analysis",
    ) -> SharedContextPayload:
        chain = self._chains.get(chain_id)
        if not chain:
            raise ValueError(f"Unknown chain: {chain_id}")

        payload = SharedContextPayload(
            chain_id=chain_id,
            from_agent=from_agent,
            to_agent=to_agent,
            artifact_type=artifact_type,
            content=artifact,
        )
        chain.payloads.append(payload)

        await self._event_bus.publish(
            Event(
                type=EventType.AGENT_COLLABORATION,
                source=AgentId.ODIN,
                correlation_id=chain_id,
                payload=payload.model_dump(mode="json"),
            )
        )
        return payload

    def build_tasks_for_chain(self, chain: CollaborationChain) -> list[Task]:
        """Build sequential tasks for orchestrator — ODIN approves execution."""
        tasks: list[Task] = []
        for i, step in enumerate(chain.steps):
            agent_id = AgentId(step["agent"])
            tasks.append(
                Task(
                    title=f"Collaboration step {i + 1}: {step['description']}",
                    description=f"{chain.objective} — {step['description']}",
                    assigned_agent=agent_id,
                    priority=TaskPriority.NORMAL,
                    metadata={
                        "chain_id": chain.id,
                        "step_index": i,
                        "collaboration": True,
                    },
                )
            )
        return tasks

    def get_chain(self, chain_id: str) -> CollaborationChain | None:
        return self._chains.get(chain_id)

    def list_chains(self) -> list[CollaborationChain]:
        return list(self._chains.values())
