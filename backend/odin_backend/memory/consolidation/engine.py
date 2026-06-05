"""Memory consolidation engine."""

import hashlib
from collections import Counter
from typing import Any

from odin_backend.events.bus import EventBus
from odin_backend.memory.coordinator import MimirCoordinator
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class MemoryConsolidationEngine:
    def __init__(self, memory: MimirCoordinator, event_bus: EventBus) -> None:
        self._memory = memory
        self._event_bus = event_bus
        self._merged_count = 0

    def _fingerprint(self, text: str) -> str:
        normalized = " ".join(text.lower().split())[:500]
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]

    async def detect_duplicates(self, memories: list[dict[str, Any]]) -> list[list[str]]:
        """Group similar memory IDs by content fingerprint."""
        buckets: dict[str, list[str]] = {}
        for m in memories:
            mid = m.get("id", m.get("memory_id", ""))
            content = m.get("content", m.get("text", ""))
            fp = self._fingerprint(str(content))
            buckets.setdefault(fp, []).append(str(mid))
        return [ids for ids in buckets.values() if len(ids) > 1]

    async def merge_similar(self, memory_ids: list[str]) -> dict[str, Any]:
        """Merge overlapping memories into consolidated entry."""
        if len(memory_ids) < 2:
            return {"merged": False}
        combined = f"[Consolidated from {len(memory_ids)} memories]"
        await self._memory.save_memory(
            combined,
            category="consolidated",
            metadata={"source_ids": memory_ids},
        )
        self._merged_count += 1
        return {"merged": True, "source_count": len(memory_ids)}

    async def summarize_project(self, project: str) -> str:
        results = await self._memory.search_memory(project, limit=20)
        if not results:
            return f"No memories found for project {project}."
        snippets = [r.get("content", r.get("text", ""))[:200] for r in results[:10]]
        return f"Project {project} summary ({len(results)} memories):\n" + "\n".join(
            f"- {s}" for s in snippets if s
        )

    async def extract_patterns(self, limit: int = 50) -> dict[str, Any]:
        results = await self._memory.search_memory("workflow", limit=limit)
        categories: Counter[str] = Counter()
        topics: Counter[str] = Counter()
        for r in results:
            cat = r.get("category", "general")
            categories[cat] += 1
            content = str(r.get("content", "")).lower()
            for word in content.split():
                if len(word) > 5:
                    topics[word] += 1

        recurring_workflows = [
            w for w, c in topics.most_common(5) if c >= 2 and "workflow" in w
        ]
        return {
            "categories": dict(categories.most_common(10)),
            "top_topics": dict(topics.most_common(10)),
            "recurring_workflows": recurring_workflows,
            "merged_total": self._merged_count,
        }

    async def strengthen_relationships(
        self,
        entity_a: str,
        entity_b: str,
        relation: str,
    ) -> None:
        await self._memory.save_memory(
            f"Relationship: {entity_a} —{relation}→ {entity_b}",
            category="relationship",
            metadata={"from": entity_a, "to": entity_b, "relation": relation},
        )
        await self._event_bus.publish(
            Event(
                type=EventType.MEMORY_CONSOLIDATED,
                source=AgentId.MIMIR,
                payload={"from": entity_a, "to": entity_b, "relation": relation},
            )
        )

    async def run_consolidation_pass(self) -> dict[str, Any]:
        results = await self._memory.search_memory("odin", limit=100)
        dup_groups = await self.detect_duplicates(results)
        merged = 0
        for group in dup_groups[:5]:
            r = await self.merge_similar(group)
            if r.get("merged"):
                merged += 1
        patterns = await self.extract_patterns()
        report = {
            "duplicate_groups": len(dup_groups),
            "merged_groups": merged,
            "patterns": patterns,
        }
        await self._event_bus.publish(
            Event(
                type=EventType.MEMORY_CONSOLIDATED,
                source=AgentId.MIMIR,
                payload=report,
            )
        )
        return report
