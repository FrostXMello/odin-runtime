"""Kernel reasoning — only entry point for LLM calls."""

from typing import TYPE_CHECKING, Any

from odin_backend.ai.models.schemas import LLMPlanResponse
from odin_backend.ai.providers.base import CompletionRequest
from odin_backend.core.model_router.router import KernelModelRouter, TaskModelType
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId
from odin_backend.models.workflow import WorkflowPlan
from odin_backend.monitoring.logging import get_logger
if TYPE_CHECKING:
    from odin_backend.orchestrator.reasoning.prompt_manager import PromptManager
    from odin_backend.orchestrator.reasoning.workflow_builder import WorkflowBuilder
    from odin_backend.core.kernel.kernel import OdinCognitiveKernel

logger = get_logger(__name__)


class KernelReasoningMixin:
    """Mixed into OdinCognitiveKernel for LLM planning."""

    _model_router: KernelModelRouter | None

    def _init_reasoning(self) -> None:
        self._model_router = None
        self._prompts: PromptManager | None = None
        self._workflow_builder: WorkflowBuilder | None = None

    def _prompts_mgr(self) -> "PromptManager":
        if self._prompts is None:
            from odin_backend.orchestrator.reasoning.prompt_manager import PromptManager

            self._prompts = PromptManager()
        return self._prompts

    def _builder(self) -> "WorkflowBuilder":
        if self._workflow_builder is None:
            from odin_backend.orchestrator.reasoning.workflow_builder import WorkflowBuilder

            self._workflow_builder = WorkflowBuilder()
        return self._workflow_builder

    def set_model_router(self, router: KernelModelRouter) -> None:
        self._model_router = router

    async def process_reasoning_request(
        self: "OdinCognitiveKernel",
        objective: str,
        *,
        context: str = "",
        correlation_id: str | None = None,
    ) -> WorkflowPlan:
        plan, trace = await self.execute_llm_planning(objective, context=context, correlation_id=correlation_id)
        self._record_live_mind(
            reasoning_trace=trace,
            model_used=trace.get("model_choice", "unknown"),
            decision_path=["reasoning", "planning", "workflow"],
        )
        await self._publish_reasoning_event(EventType.REASONING_COMPLETED, plan, correlation_id)
        return plan

    async def execute_llm_planning(
        self: "OdinCognitiveKernel",
        objective: str,
        *,
        context: str = "",
        correlation_id: str | None = None,
    ) -> tuple[WorkflowPlan, dict[str, Any]]:
        await self._publish_reasoning_event(
            EventType.REASONING_STARTED,
            None,
            correlation_id,
            payload={"objective": objective},
        )
        routing = await self.fallback_reasoning_chain(objective, context)
        trace = {
            "objective": objective,
            "model_choice": routing.get("model_choice"),
            "confidence": routing.get("confidence_score"),
            "fallback_used": routing.get("fallback_used"),
        }

        if routing.get("plan"):
            return routing["plan"], trace

        plan = self._builder().from_rule_based(objective, correlation_id)
        trace["model_choice"] = routing.get("model_choice", "rule-based")
        trace["summary"] = routing.get("summary")
        return plan, trace

    async def fallback_reasoning_chain(
        self: "OdinCognitiveKernel",
        objective: str,
        context: str,
    ) -> dict[str, Any]:
        if not self._model_router:
            return {"plan": self._builder().from_rule_based(objective, None)}

        messages = self._prompts_mgr().build_planning_messages(objective, context)
        for task_type in (TaskModelType.PLANNING, TaskModelType.REASONING, TaskModelType.CONVERSATIONAL):
            result = await self._model_router.route_and_complete(messages, task_type)
            try:
                import json

                parsed = json.loads(result.reasoning_response)
                validated = LLMPlanResponse.model_validate(parsed)
                plan = self._builder().from_llm_json(validated.to_dict(), None)
                return {
                    "plan": plan,
                    "model_choice": result.model_choice,
                    "confidence_score": result.confidence_score,
                    "fallback_used": result.fallback_used,
                }
            except Exception:
                if len(result.reasoning_response) > 20 and task_type == TaskModelType.SUMMARIZATION:
                    break
                logger.debug("reasoning_json_parse_retry", task_type=task_type.value)

        summary = await self._model_router.route_and_complete(
            [
                {"role": "system", "content": "Summarize and list actionable steps as JSON plan."},
                {"role": "user", "content": f"{objective}\n{context}"},
            ],
            TaskModelType.SUMMARIZATION,
        )
        return {
            "model_choice": summary.model_choice,
            "confidence_score": summary.confidence_score,
            "fallback_used": summary.fallback_used,
            "summary": summary.reasoning_response,
        }

    def _record_live_mind(self: "OdinCognitiveKernel", **fields: Any) -> None:
        if "reasoning_trace" in fields:
            traces = list(self._state.reasoning_trace)
            traces.append(fields["reasoning_trace"])
            self._state.reasoning_trace = traces[-20:]
        if "model_used" in fields:
            self._state.model_used = fields["model_used"]
        if "decision_path" in fields:
            self._state.decision_path = fields["decision_path"]

    async def _publish_reasoning_event(
        self: "OdinCognitiveKernel",
        event_type: EventType,
        plan: WorkflowPlan | None,
        correlation_id: str | None,
        payload: dict | None = None,
    ) -> None:
        from odin_backend.core.bus.unified_bus import SignalUnificationBus

        body = payload or {}
        if plan:
            body = {"plan_id": plan.id, "objective": plan.objective, "step_count": len(plan.steps)}
        event = Event(
            type=event_type,
            source=AgentId.ODIN,
            correlation_id=correlation_id,
            payload=body,
        )
        if isinstance(self._event_bus, SignalUnificationBus):
            await self._event_bus.inner.publish(event)
        else:
            await self._event_bus.publish(event)
