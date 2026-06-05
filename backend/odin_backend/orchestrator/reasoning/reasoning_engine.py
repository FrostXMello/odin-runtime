"""ODIN reasoning engine — analyze intent, produce structured plans."""

from odin_backend.ai.routing.intelligent_router import IntelligentModelRouter
from odin_backend.config import Settings
from odin_backend.events.bus import EventBus
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId
from odin_backend.models.workflow import WorkflowPlan
from odin_backend.monitoring.logging import get_logger
from odin_backend.models.trace import TraceContext
from odin_backend.orchestrator.reasoning.planner import Planner

logger = get_logger(__name__)


class ReasoningEngine:
    """
    Receives objectives, analyzes intent, generates structured execution plans.
    Does NOT execute tools — output flows to workflow engine.
    """

    def __init__(self, settings: Settings, event_bus: EventBus, cognition=None) -> None:
        self._settings = settings
        self._event_bus = event_bus
        self._router = IntelligentModelRouter(settings)
        self._planner = Planner(self._router)
        self._cognition = cognition
        self._kernel = None

    def set_kernel(self, kernel) -> None:
        """Kernel is the sole LLM entry point when set."""
        self._kernel = kernel

    async def reason(
        self,
        objective: str,
        *,
        context: str = "",
        correlation_id: str | None = None,
    ) -> WorkflowPlan:
        trace = TraceContext(correlation_id=correlation_id)
        if self._cognition:
            await self._cognition.emit("Analyzing objective", stage="reasoning.start", trace=trace)
            await self._cognition.emit("Retrieving related memory", stage="memory.retrieve", trace=trace)
        await self._event_bus.publish(
            Event(
                type=EventType.REASONING_STARTED,
                source=AgentId.ODIN,
                correlation_id=correlation_id,
                payload={"objective": objective},
            )
        )

        if self._cognition:
            await self._cognition.emit("Generating workflow plan", stage="planning.generate", trace=trace)
        if self._kernel is not None:
            plan = await self._kernel.process_reasoning_request(
                objective, context=context, correlation_id=correlation_id
            )
        else:
            plan = await self._planner.create_plan(objective, context, correlation_id)
            await self._event_bus.publish(
                Event(
                    type=EventType.REASONING_COMPLETED,
                    source=AgentId.ODIN,
                    correlation_id=correlation_id,
                    payload={
                        "plan_id": plan.id,
                        "objective": plan.objective,
                        "step_count": len(plan.steps),
                    },
                )
            )
        if self._cognition:
            await self._cognition.emit(
                f"Plan ready with {len(plan.steps)} steps",
                stage="planning.completed",
                trace=trace,
            )
        logger.info("reasoning_completed", plan_id=plan.id, steps=len(plan.steps))
        return plan
