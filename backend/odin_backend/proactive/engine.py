"""Proactive recommendation engine — suggest only, never auto-execute."""

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from odin_backend.context_engine.engine import ContextEngine
from odin_backend.desktop_semantics.service import DesktopSemanticsService
from odin_backend.events.bus import EventBus
from odin_backend.execution_intelligence.service import ExecutionIntelligenceService
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class Recommendation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    message: str
    category: str  # research | workflow | memory | optimization | archive
    relevance: float = 0.5
    urgency: float = 0.3
    confidence: float = 0.7
    workflow_importance: float = 0.5
    explainable: dict[str, Any] = Field(default_factory=dict)
    dismissed: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def priority_score(self) -> float:
        return (
            self.relevance * 0.35
            + self.urgency * 0.25
            + self.confidence * 0.2
            + self.workflow_importance * 0.2
        )


class ProactiveAssistanceEngine:
    def __init__(
        self,
        event_bus: EventBus,
        context_engine: ContextEngine,
        desktop: DesktopSemanticsService,
        execution_intel: ExecutionIntelligenceService,
    ) -> None:
        self._event_bus = event_bus
        self._context = context_engine
        self._desktop = desktop
        self._execution = execution_intel
        self._recommendations: dict[str, Recommendation] = {}

    async def generate_recommendations(self) -> list[Recommendation]:
        recs: list[Recommendation] = []
        ctx = self._context.get_session()

        if ctx and ctx.browser_tabs and len(ctx.browser_tabs) >= 3:
            recs.append(
                Recommendation(
                    title="Summarize research tabs",
                    message="These tabs appear related to your current research session.",
                    category="research",
                    relevance=0.8,
                    urgency=0.4,
                    confidence=0.75,
                    explainable={
                        "source": "browser_tabs",
                        "tab_count": len(ctx.browser_tabs),
                        "reason": "Multiple related tabs detected",
                    },
                )
            )

        if ctx:
            summary = self._desktop.summarize_current_workspace(ctx)
            if summary.get("session_type") == "development":
                recs.append(
                    Recommendation(
                        title="Inspect repository architecture",
                        message=f"Active development on {summary.get('detected_project', ctx.project)}.",
                        category="workflow",
                        relevance=0.7,
                        confidence=0.8,
                        explainable={"source": "desktop_semantics", **summary.get("explainable", {})},
                    )
                )

        scores = self._execution.get_reliability_scores()
        degraded = [s for s in scores if s.get("success_rate", 1) < 0.6 and s.get("sample_size", 0) >= 3]
        for s in degraded[:2]:
            recs.append(
                Recommendation(
                    title="Workflow optimization suggested",
                    message=f"Recent workflows repeatedly had issues with {s['tool_name']}.",
                    category="optimization",
                    relevance=0.85,
                    urgency=0.6,
                    confidence=0.9,
                    workflow_importance=0.8,
                    explainable={"source": "execution_intelligence", "tool": s["tool_name"]},
                )
            )

        if ctx and len(ctx.recent_interactions) > 10:
            recs.append(
                Recommendation(
                    title="Archive session context",
                    message="Consider saving a context snapshot for this extended session.",
                    category="archive",
                    relevance=0.5,
                    urgency=0.2,
                    confidence=0.65,
                    explainable={"source": "interaction_count", "count": len(ctx.recent_interactions)},
                )
            )

        recs.sort(key=lambda r: r.priority_score, reverse=True)
        for r in recs:
            self._recommendations[r.id] = r
            await self._emit(r)
        return recs

    async def _emit(self, rec: Recommendation) -> None:
        await self._event_bus.publish(
            Event(
                type=EventType.RECOMMENDATION_CREATED,
                source=AgentId.ODIN,
                payload=rec.model_dump(mode="json"),
            )
        )

    def list_recommendations(self, include_dismissed: bool = False) -> list[Recommendation]:
        items = list(self._recommendations.values())
        if not include_dismissed:
            items = [r for r in items if not r.dismissed]
        return sorted(items, key=lambda r: r.priority_score, reverse=True)

    def dismiss(self, recommendation_id: str) -> bool:
        rec = self._recommendations.get(recommendation_id)
        if rec:
            rec.dismissed = True
            return True
        return False

    def explain(self, recommendation_id: str) -> dict[str, Any] | None:
        rec = self._recommendations.get(recommendation_id)
        if not rec:
            return None
        return {
            "title": rec.title,
            "message": rec.message,
            "priority_score": rec.priority_score,
            "explainable": rec.explainable,
            "requires_approval_to_execute": True,
        }
