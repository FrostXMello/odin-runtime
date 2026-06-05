"""Dynamic context assembly for local reasoning."""

from __future__ import annotations

from typing import Any

from odin_backend.core.cognition.reasoning.relevance_scoring import rank_items
from odin_backend.core.cognition.reasoning.semantic_grounding import format_grounding_block
from odin_backend.core.models.context_windowing import truncate_text
from odin_backend.core.models.tokenizer import estimate_tokens


class ReasoningContextBuilder:
    def __init__(self, app: Any) -> None:
        self._app = app

    async def build(
        self,
        *,
        objective: str,
        mission_id: str | None = None,
        max_tokens: int = 4096,
    ) -> dict[str, Any]:
        retrieval = getattr(self._app, "memory_retrieval", None)
        intel = getattr(self._app, "execution_intelligence", None)
        similar: list[dict] = []
        failures: list[dict] = []
        strategies: list[dict] = []
        if retrieval:
            similar = rank_items(objective, await retrieval.similar_executions(objective, limit=8))
            failures = await retrieval.failure_patterns(limit=5)
            strategies = await retrieval.recall_strategy(objective[:40])
        cap_stats = intel.capability_scores() if intel else {}
        block = format_grounding_block(
            similar=similar,
            failures=failures,
            strategies=strategies,
            capability_stats=cap_stats,
        )
        truncated = False
        if estimate_tokens(block) > max_tokens:
            block, truncated = truncate_text(block, max_tokens=max_tokens)
        if truncated:
            self._emit("context_truncated", {"mission_id": mission_id})
        self._emit("memory_grounded", {"similar": len(similar), "failures": len(failures)}, mission_id=mission_id)
        return {
            "objective": objective,
            "mission_id": mission_id,
            "prompt_block": block,
            "similar_executions": similar,
            "failure_patterns": failures,
            "strategies": strategies,
            "capability_stats": cap_stats,
            "truncated": truncated,
        }

    def _emit(self, kind_name: str, payload: dict, *, mission_id: str | None = None) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        if mission_id:
            payload = {**payload, "mission_id": mission_id}
        obs.tracer.record(kind, message=kind_name, payload=payload, component="reasoning_context")
