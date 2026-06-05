"""Longitudinal memory intelligence and behavioral timelines."""

from collections import Counter
from datetime import datetime, timezone
from typing import Any

from odin_backend.events.bus import EventBus
from odin_backend.memory.coordinator import MimirCoordinator
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId


class MemoryEvolutionEngine:
    def __init__(self, memory: MimirCoordinator, event_bus: EventBus) -> None:
        self._memory = memory
        self._event_bus = event_bus
        self._timeline: list[dict[str, Any]] = []

    async def record_operational_event(self, event_type: str, detail: str, metadata: dict | None = None) -> None:
        entry = {
            "type": event_type,
            "detail": detail,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {},
        }
        self._timeline.append(entry)
        if len(self._timeline) > 1000:
            self._timeline = self._timeline[-1000:]
        await self._memory.save_memory(
            f"[{event_type}] {detail}",
            category="operational_timeline",
            metadata=metadata,
        )

    async def generate_weekly_summary(self) -> str:
        results = await self._memory.search_memory("operational", limit=30)
        if not results:
            return "No operational events recorded this period."
        lines = [r.get("content", "")[:150] for r in results[:15]]
        return "Weekly operational summary:\n" + "\n".join(f"- {l}" for l in lines if l)

    async def extract_long_term_patterns(self) -> dict[str, Any]:
        results = await self._memory.search_memory("workflow", limit=50)
        projects: Counter[str] = Counter()
        for r in results:
            proj = r.get("metadata", {}).get("project", "unknown")
            projects[proj] += 1
        return {
            "recurring_projects": dict(projects.most_common(5)),
            "timeline_entries": len(self._timeline),
            "patterns_detected": len(projects),
        }

    async def strengthen_relationship(self, entity_a: str, entity_b: str, relation: str) -> None:
        await self._memory.save_memory(
            f"Evolved relationship: {entity_a} —{relation}→ {entity_b}",
            category="relationship_evolution",
            metadata={"from": entity_a, "to": entity_b, "relation": relation},
        )
        await self._event_bus.publish(
            Event(
                type=EventType.MEMORY_EVOLUTION_UPDATED,
                source=AgentId.MIMIR,
                payload={"from": entity_a, "to": entity_b, "relation": relation},
            )
        )

    def get_behavioral_timeline(self, limit: int = 50) -> list[dict[str, Any]]:
        return list(reversed(self._timeline[-limit:]))

    async def replay_historical_context(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        return await self._memory.search_memory(query, limit=limit)
