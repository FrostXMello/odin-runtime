"""Perception-aware memory — outcome chains and failure patterns."""

from typing import Any

from odin_backend.models.perception import PerceptionRecord


class PerceptionMemoryStore:
    def __init__(self, memory_coordinator: Any) -> None:
        self._memory = memory_coordinator
        self._history: list[dict[str, Any]] = []
        self._failure_patterns: dict[str, int] = {}
        self._strategy_records: list[dict[str, Any]] = []

    async def record_perception(self, record: PerceptionRecord) -> str:
        mem_id = await self._memory.save_memory(
            record.summary or record.category.value,
            category="perception",
            metadata={
                "perception_id": record.id,
                "category": record.category.value,
                "mission_id": record.mission_id,
                "task_id": record.task_id,
                "tool": record.tool,
                **record.payload,
            },
        )
        entry = record.model_dump(mode="json")
        entry["memory_id"] = mem_id
        self._history.append(entry)
        if len(self._history) > 2000:
            self._history = self._history[-2000:]
        if record.category.value.endswith("failure.detected"):
            key = f"{record.tool}:{record.payload.get('failure_class', 'unknown')}"
            self._failure_patterns[key] = self._failure_patterns.get(key, 0) + 1
        return mem_id

    async def record_outcome_chain(
        self,
        mission_id: str,
        chain: list[dict[str, Any]],
    ) -> None:
        await self._memory.save_memory(
            f"Outcome chain for mission {mission_id}",
            category="perception",
            metadata={"mission_id": mission_id, "chain": chain, "kind": "outcome_chain"},
        )

    def record_strategy(self, mission_id: str, strategy: str, *, reason: str) -> None:
        self._strategy_records.append(
            {
                "mission_id": mission_id,
                "strategy": strategy,
                "reason": reason,
            }
        )
        if len(self._strategy_records) > 500:
            self._strategy_records = self._strategy_records[-500:]

    def history(self, limit: int = 100, *, mission_id: str | None = None) -> list[dict[str, Any]]:
        items = self._history
        if mission_id:
            items = [h for h in items if h.get("mission_id") == mission_id]
        return list(reversed(items[-limit:]))

    def failure_patterns(self) -> dict[str, int]:
        return dict(self._failure_patterns)

    def strategies_for(self, mission_id: str) -> list[dict[str, Any]]:
        return [s for s in self._strategy_records if s.get("mission_id") == mission_id]
