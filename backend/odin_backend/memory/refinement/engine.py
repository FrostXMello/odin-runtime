"""Memory refinement — traceable merge, compress, rank."""

import hashlib
from typing import Any

from pydantic import BaseModel, Field

from odin_backend.events.bus import EventBus
from odin_backend.memory.coordinator import MimirCoordinator
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class RefinementReport(BaseModel):
    merged_count: int = 0
    pruned_stale: int = 0
    compressed_entries: int = 0
    reinforced_links: int = 0
    pruning_report: list[str] = Field(default_factory=list)
    compression_summary: str = ""
    trace_log: list[str] = Field(default_factory=list)


class MemoryRefinementEngine:
    """No destructive deletion without trace logging."""

    def __init__(self, memory: MimirCoordinator, event_bus: EventBus) -> None:
        self._memory = memory
        self._event_bus = event_bus
        self._archived_ids: list[str] = []

    def _fingerprint(self, text: str) -> str:
        return hashlib.sha256(text.lower().strip().encode()).hexdigest()[:16]

    async def refine(self, limit: int = 100) -> RefinementReport:
        report = RefinementReport()
        results = await self._memory.search_memory("odin", limit=limit)
        buckets: dict[str, list[dict]] = {}

        for r in results:
            content = str(r.get("content", ""))
            fp = self._fingerprint(content)
            buckets.setdefault(fp, []).append(r)

        for fp, group in buckets.items():
            if len(group) > 1:
                ids = [str(g.get("id", g.get("memory_id", ""))) for g in group]
                report.merged_count += len(group) - 1
                msg = f"Merged duplicate memories: {ids} → archived (not deleted)"
                report.pruning_report.append(msg)
                report.trace_log.append(msg)
                self._archived_ids.extend(ids[1:])
                await self._memory.save_memory(
                    f"[refined merge] {group[0].get('content', '')[:200]}",
                    category="refined",
                    metadata={"merged_from": ids, "fingerprint": fp},
                )

        # Compress long histories
        wf_memories = [r for r in results if r.get("category") == "workflow"]
        if len(wf_memories) > 20:
            report.compressed_entries = len(wf_memories) - 20
            report.compression_summary = f"Compressed {report.compressed_entries} workflow history entries into summary"
            report.trace_log.append(report.compression_summary)
            summary = " | ".join(str(m.get("content", ""))[:60] for m in wf_memories[:5])
            await self._memory.save_memory(
                f"[compressed workflow history] {summary}",
                category="compressed",
            )

        # Reinforce high-utility links
        for r in results[:5]:
            mid = r.get("id")
            if mid:
                report.reinforced_links += 1
                await self._memory.save_memory(
                    f"[reinforced] {r.get('content', '')[:100]}",
                    category="reinforced",
                    metadata={"reinforced_from": str(mid)},
                )

        await self._event_bus.publish(
            Event(
                type=EventType.MEMORY_REFINED,
                source=AgentId.MIMIR,
                payload=report.model_dump(),
            )
        )
        logger.info("memory_refinement_complete", merged=report.merged_count)
        return report
