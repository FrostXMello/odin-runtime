"""Mission-scoped planner context assembly."""

from __future__ import annotations

from typing import Any

from odin_backend.core.memory.context.execution_history import ExecutionHistoryIndex
from odin_backend.core.memory.context.retrieval import PlannerRetriever
from odin_backend.core.memory.context.semantic_memory import SemanticMemoryEntry
from odin_backend.models.mission import Mission


class MissionContextService:
    def __init__(self, app: Any) -> None:
        self._app = app
        settings = app.settings
        self.history = ExecutionHistoryIndex(settings)
        self.retriever = PlannerRetriever()
        self._connected = False

    async def connect(self) -> None:
        await self.history.connect()
        self._connected = True

    async def disconnect(self) -> None:
        await self.history.disconnect()
        self._connected = False

    async def build_context(self, mission: Mission) -> dict[str, Any]:
        hist = await self.history.list_for_mission(mission.mission_id)
        failures = await self.history.failure_count(mission.mission_id)
        hits = self.retriever.retrieve(mission.objective, mission_id=mission.mission_id, limit=5)
        global_hits = self.retriever.retrieve(mission.objective, mission_id=None, limit=3)

        summary_parts = []
        if hits:
            summary_parts.append(f"{len(hits)} similar mission memories")
        if failures:
            summary_parts.append(f"{failures} prior failures in mission")
        if hist:
            summary_parts.append(f"{len(hist)} history events")

        return {
            "summary": "; ".join(summary_parts) if summary_parts else "",
            "memory_hits": len(hits) + len(global_hits),
            "prior_failures": failures,
            "semantic_hits": hits,
            "global_hits": global_hits,
            "history": hist[:10],
        }

    async def record_outcome(
        self,
        mission_id: str,
        *,
        capability: str,
        tool_name: str | None,
        success: bool,
        summary: str,
    ) -> None:
        await self.history.append(
            mission_id,
            "execution_outcome",
            summary,
            capability=capability,
            tool_name=tool_name,
            success=success,
        )
        self.retriever.index(
            SemanticMemoryEntry(
                mission_id=mission_id,
                text=summary,
                kind="outcome" if success else "failure",
                score=0.8 if success else 0.2,
                metadata={"capability": capability, "tool": tool_name},
            )
        )
        tm = getattr(self._app, "tool_memory", None)
        if tm and tool_name:
            await tm.record(mission_id, capability, tool_name, success=success)
