"""Desktop semantics — graph, classification, workspace summaries."""

from typing import Any

from odin_backend.context_engine.sessions import UnifiedContextSession
from odin_backend.desktop_semantics.classifier import SemanticClassifier, SessionType
from odin_backend.desktop_semantics.graph import DesktopGraph
from odin_backend.events.bus import EventBus
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class DesktopSemanticsService:
    """Interpret desktop environment — observation only, no auto-control."""

    def __init__(self, event_bus: EventBus) -> None:
        self._event_bus = event_bus
        self._classifier = SemanticClassifier()
        self._last_graph: DesktopGraph | None = None
        self._last_session_type: SessionType = SessionType.GENERAL

    def build_graph_from_context(self, ctx: UnifiedContextSession) -> DesktopGraph:
        graph = DesktopGraph()
        app_nodes: dict[str, str] = {}

        for app in ctx.active_applications:
            node = graph.add_entity("app", app.name, window=app.window_title)
            app_nodes[app.name] = node.id

        tab_nodes = []
        for tab in ctx.browser_tabs:
            node = graph.add_entity("tab", tab.title or tab.url, url=tab.url)
            tab_nodes.append(node)

        term_nodes = []
        for term in ctx.terminals:
            node = graph.add_entity("terminal", term.cwd or "shell", cwd=term.cwd)
            term_nodes.append(node)

        if ctx.repository_path:
            repo = graph.add_entity("file", ctx.repository_path, kind="repository")
            for tn in term_nodes:
                graph.link(repo.id, tn.id, "executes_in")
            for an in app_nodes.values():
                graph.link(repo.id, an, "edited_in")

        for wf_id in ctx.active_workflow_ids:
            wf = graph.add_entity("workflow", wf_id)
            if app_nodes:
                first_app = next(iter(app_nodes.values()))
                graph.link(wf, first_app, "triggered_from")

        self._last_graph = graph
        return graph

    def summarize_current_workspace(self, ctx: UnifiedContextSession | None) -> dict[str, Any]:
        if not ctx:
            return {"summary": "No desktop context available.", "session_type": "general"}

        windows = [
            {"title": a.window_title or a.name, "app": a.name}
            for a in ctx.active_applications
        ]
        session_type = self._classifier.classify_session(windows)
        self._last_session_type = session_type
        graph = self.build_graph_from_context(ctx)

        clusters = self.cluster_related_windows(ctx)
        project = self.detect_active_project(ctx)

        return {
            "summary": ctx.insight or f"Active {session_type.value} session for {ctx.project}",
            "session_type": session_type.value,
            "detected_project": project,
            "entity_count": len(graph.entities),
            "clusters": clusters,
            "explainable": {
                "classification_basis": [w.get("title") for w in windows[:5]],
                "tab_count": len(ctx.browser_tabs),
                "terminal_count": len(ctx.terminals),
            },
        }

    def detect_active_project(self, ctx: UnifiedContextSession) -> str:
        if ctx.repository_path:
            return ctx.repository_path.split("/")[-1].split("\\")[-1]
        for tab in ctx.browser_tabs:
            if "github.com" in tab.url.lower():
                parts = tab.url.rstrip("/").split("/")
                if len(parts) >= 2:
                    return parts[-1]
        return ctx.project

    def cluster_related_windows(self, ctx: UnifiedContextSession) -> list[dict[str, Any]]:
        clusters: list[dict[str, Any]] = []
        if ctx.active_applications and ctx.terminals:
            clusters.append({
                "label": "dev_stack",
                "members": ["ide", "terminal"],
                "reason": "IDE and terminal co-active",
            })
        gh_tabs = [t for t in ctx.browser_tabs if "github" in t.url.lower()]
        if gh_tabs and ctx.repository_path:
            clusters.append({
                "label": "repo_research",
                "members": ["browser", "repository"],
                "reason": "GitHub tabs align with open repository",
            })
        return clusters

    async def emit_analysis(self, summary: dict[str, Any]) -> None:
        await self._event_bus.publish(
            Event(
                type=EventType.DESKTOP_SEMANTICS_UPDATED,
                source=AgentId.ODIN,
                payload=summary,
            )
        )
