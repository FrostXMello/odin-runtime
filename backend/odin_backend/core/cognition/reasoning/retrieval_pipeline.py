"""Hybrid retrieval pipeline for memory-grounded reasoning."""

from __future__ import annotations

from typing import Any

from odin_backend.core.cognition.reasoning.chain_assembly import assemble_chain
from odin_backend.core.cognition.reasoning.context_builder import ReasoningContextBuilder
from odin_backend.core.cognition.reasoning.memory_prompting import build_reasoning_prompt
from odin_backend.core.cognition.reasoning.relevance_scoring import rank_items


class ReasoningPipeline:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._context_builder = ReasoningContextBuilder(app)

    async def build(self, *, objective: str, mission_id: str | None = None) -> dict[str, Any]:
        return await self._context_builder.build(objective=objective, mission_id=mission_id)

    async def run(
        self,
        *,
        objective: str,
        mission_id: str | None = None,
    ) -> dict[str, Any]:
        ctx = await self.build(objective=objective, mission_id=mission_id)
        messages = build_reasoning_prompt(objective=objective, grounding=ctx["prompt_block"])
        model = self._app.model_manager.runtime.router.select_model(
            capability=__import__(
                "odin_backend.core.models.model_profiles", fromlist=["ModelCapabilityTag"]
            ).ModelCapabilityTag.REASONING,
        )
        response = await self._app.model_manager.runtime.infer(
            messages=messages,
            model=model,
            task_kind="planning",
            mission_id=mission_id,
        )
        chain_steps: list[dict] = []
        if mission_id and hasattr(self._app, "cognitive_agents"):
            pipeline = await self._app.cognitive_agents.run_pipeline(objective=objective, mission_id=mission_id)
            chain_steps = pipeline.get("steps", [])
        hybrid_hits: list[dict] = []
        embed = getattr(self._app, "embedding_runtime", None)
        if embed:
            hybrid_hits = await embed.hybrid_search(objective, limit=5)
            hybrid_hits = rank_items(objective, hybrid_hits)
        return {
            "objective": objective,
            "mission_id": mission_id,
            "model": model,
            "response": response,
            "context": ctx,
            "hybrid_hits": hybrid_hits,
            "chain": assemble_chain(chain_steps) if chain_steps else None,
        }
