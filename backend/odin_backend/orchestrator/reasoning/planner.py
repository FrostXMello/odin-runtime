"""Planning coordinator — LLM or rule-based."""

from odin_backend.ai.models.schemas import LLMPlanResponse
from odin_backend.ai.providers.base import CompletionRequest
from odin_backend.ai.routing.intelligent_router import IntelligentModelRouter
from odin_backend.models.workflow import WorkflowPlan
from odin_backend.monitoring.logging import get_logger
from odin_backend.orchestrator.reasoning.prompt_manager import PromptManager
from odin_backend.orchestrator.reasoning.workflow_builder import WorkflowBuilder

logger = get_logger(__name__)


class Planner:
    def __init__(self, router: IntelligentModelRouter) -> None:
        self._router = router
        self._prompts = PromptManager()
        self._builder = WorkflowBuilder()

    async def create_plan(
        self, objective: str, context: str = "", correlation_id: str | None = None
    ) -> WorkflowPlan:
        if self._router._openai.available:  # noqa: SLF001 — planning prefers cloud when available
            try:
                messages = self._prompts.build_planning_messages(objective, context)
                raw = await self._router._openai.complete_json(  # noqa: SLF001
                    CompletionRequest(messages=messages, temperature=0.1)
                )
                validated = LLMPlanResponse.model_validate(raw)
                plan = self._builder.from_llm_json(validated.to_dict(), correlation_id)
                logger.info("plan_created_llm", steps=len(plan.steps))
                return plan
            except Exception as exc:
                logger.warning("llm_plan_failed_fallback", error=str(exc))

        plan = self._builder.from_rule_based(objective, correlation_id)
        logger.info("plan_created_rules", steps=len(plan.steps))
        return plan
