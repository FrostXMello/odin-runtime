"""Live cognition — continuous operational state."""

from typing import Any

from odin_backend.cognitive_stream.aggregator import UnifiedCognitiveStream
from odin_backend.context_engine.engine import ContextEngine
from odin_backend.events.bus import EventBus
from odin_backend.live_cognition.attention import AttentionPriority, CognitiveAttentionSystem
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId
from odin_backend.workspace_intelligence.engine import WorkspaceIntelligenceEngine


class LiveCognitionEngine:
    def __init__(
        self,
        event_bus: EventBus,
        unified: UnifiedCognitiveStream,
        context_engine: ContextEngine,
        workspace: WorkspaceIntelligenceEngine,
    ) -> None:
        self._event_bus = event_bus
        self._unified = unified
        self._context = context_engine
        self._workspace = workspace
        self._attention = CognitiveAttentionSystem()
        self._focus_graph: dict[str, list[str]] = {}
        self._goals: list[str] = []

    def get_current_attention(self) -> list[dict[str, Any]]:
        return [a.model_dump() for a in self._attention.get_current_attention()]

    def summarize_operational_state(self) -> dict[str, Any]:
        ctx = self._context.get_session()
        ws = self._workspace.summarize_workspace(ctx)
        attention = self.get_current_attention()
        return {
            "workspace": ws,
            "attention_top": attention[:5],
            "active_goals": self._goals,
            "focus_graph": self._focus_graph,
            "timeline_preview": self._unified.timeline(10),
        }

    def get_active_focus_graph(self) -> dict[str, Any]:
        ctx = self._context.get_session()
        if not ctx:
            return {"nodes": [], "edges": []}
        nodes = []
        edges = []
        if ctx.repository_path:
            nodes.append({"id": "repo", "label": ctx.repository_path})
        for i, tab in enumerate(ctx.browser_tabs[:5]):
            nid = f"tab_{i}"
            nodes.append({"id": nid, "label": tab.title or tab.url})
            if ctx.repository_path:
                edges.append({"from": "repo", "to": nid, "relation": "research"})
        for wf in ctx.active_workflow_ids:
            nodes.append({"id": wf, "label": f"workflow:{wf[:8]}"})
            edges.append({"from": "repo", "to": wf, "relation": "executes"})
        self._focus_graph = {"nodes": nodes, "edges": edges}
        return self._focus_graph

    async def ingest_context_shift(self, insight: str) -> None:
        self._attention.on_context_shift(insight)
        from odin_backend.cognitive_stream.aggregator import CognitiveSource

        await self._unified.ingest(
            insight,
            source=CognitiveSource.CONTEXT_SHIFT,
            stage="live.context_shift",
        )

    async def ingest_workflow_failure(self, workflow_id: str, error: str) -> None:
        self._attention.on_workflow_failure(workflow_id, error)
        await self._event_bus.publish(
            Event(
                type=EventType.LIVE_COGNITION_UPDATED,
                source=AgentId.ODIN,
                workflow_id=workflow_id,
                payload={"type": "workflow_failure", "error": error},
            )
        )

    def set_active_goals(self, goals: list[str]) -> None:
        self._goals = goals
