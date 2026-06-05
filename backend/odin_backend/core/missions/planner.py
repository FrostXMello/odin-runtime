"""Mission planner — semantic planning bound to mission lifecycle."""

from __future__ import annotations

from typing import Any

from odin_backend.core.planning.horizon import HorizonPlan
from odin_backend.core.planning.semantic_planner import SemanticMissionPlan, SemanticPlanner
from odin_backend.models.mission import Mission, MissionLifecycle


class MissionPlanner:
    def __init__(self, app: Any | None = None) -> None:
        self._semantic = SemanticPlanner(app)
        self._app = app

    @property
    def semantic(self) -> SemanticPlanner:
        return self._semantic

    async def _context_for(self, mission: Mission) -> dict[str, Any]:
        ctx_svc = getattr(self._app, "mission_context", None) if self._app else None
        if not ctx_svc:
            return {"summary": "", "memory_hits": 0, "prior_failures": 0}
        return await ctx_svc.build_context(mission)

    def plan(self, mission: Mission) -> HorizonPlan:
        import asyncio

        ctx: dict[str, Any] = {}
        if self._app and getattr(self._app, "mission_context", None):
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    ctx = {"summary": "", "memory_hits": 0, "prior_failures": 0}
                else:
                    ctx = loop.run_until_complete(self._context_for(mission))
            except RuntimeError:
                ctx = {"summary": "", "memory_hits": 0, "prior_failures": 0}
        else:
            ctx = {"summary": "", "memory_hits": 0, "prior_failures": 0}

        semantic = self._semantic.plan(
            mission,
            context_summary=ctx.get("summary", ""),
            memory_hits=int(ctx.get("memory_hits", 0)),
            prior_failures=int(ctx.get("prior_failures", 0)),
        )
        self._apply_semantic_plan(mission, semantic)
        return semantic.to_horizon_plan()

    async def plan_async(self, mission: Mission) -> HorizonPlan:
        ctx = await self._context_for(mission)
        semantic = self._semantic.plan(
            mission,
            context_summary=ctx.get("summary", ""),
            memory_hits=int(ctx.get("memory_hits", 0)),
            prior_failures=int(ctx.get("prior_failures", 0)),
        )
        self._apply_semantic_plan(mission, semantic)
        return semantic.to_horizon_plan()

    def replan(self, mission: Mission, *, reason: str = "reevaluation") -> HorizonPlan:
        semantic = self._semantic.replan(mission, reason=reason)
        self._apply_semantic_plan(mission, semantic, replan=True)
        return semantic.to_horizon_plan()

    def expand(
        self,
        mission: Mission,
        *,
        follow_up_goal: str,
        after_task_id: str | None = None,
    ):
        return self._semantic.expand_graph(mission, follow_up_goal=follow_up_goal, after_task_id=after_task_id)

    def get_semantic_plan(self, mission_id: str) -> SemanticMissionPlan | None:
        return self._semantic.get_plan(mission_id)

    def _apply_semantic_plan(
        self,
        mission: Mission,
        semantic: SemanticMissionPlan,
        *,
        replan: bool = False,
    ) -> None:
        mission.task_graph = semantic.task_graph
        mission.current_state = MissionLifecycle.PLANNING
        mission.execution_strategy = semantic.strategy.get("kind", mission.execution_strategy)
        mission.confidence = semantic.confidence
        mission.metadata["semantic_plan"] = {
            "parsed": semantic.parsed,
            "strategy": semantic.strategy,
            "reasoning": semantic.reasoning,
            "confidence_actions": semantic.confidence_actions,
            "capability_requirements": semantic.capability_requirements,
        }
        mission.metadata["planner_contracts"] = semantic.contracts
        mission.append_reasoning(
            "mission_replanned" if replan else "mission_planned",
            detail={
                "waves": len(semantic.waves),
                "milestones": semantic.milestones,
                "node_count": len(semantic.task_graph.nodes),
                "confidence": semantic.confidence,
                "strategy": semantic.strategy.get("kind"),
            },
        )
        mission.sync_task_lists()

        if self._app:
            validator = getattr(self._app, "plan_validator", None)
            if validator:
                v = validator.validate_plan(semantic.task_graph, semantic.contracts)
                if not v["consistent"]:
                    mission.append_reasoning("plan_validation_warning", detail=v)
