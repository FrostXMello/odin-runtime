"""Workspace intelligence engine."""

from typing import Any

from odin_backend.context_engine.sessions import UnifiedContextSession
from odin_backend.events.bus import EventBus
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId
from odin_backend.workspace_intelligence.classifier import WorkspaceClassifier, WorkspaceSessionType


class WorkspaceIntelligenceEngine:
    def __init__(self, event_bus: EventBus) -> None:
        self._event_bus = event_bus
        self._classifier = WorkspaceClassifier()
        self._active_repo: str | None = None
        self._linked_workflows: list[str] = []
        self._objectives: list[str] = []

    def track_project(
        self,
        repository: str | None = None,
        workflow_ids: list[str] | None = None,
        objectives: list[str] | None = None,
    ) -> None:
        if repository:
            self._active_repo = repository
        if workflow_ids:
            self._linked_workflows = workflow_ids
        if objectives:
            self._objectives = objectives

    def summarize_workspace(self, ctx: UnifiedContextSession | None) -> dict[str, Any]:
        if not ctx:
            return {"summary": "No workspace context.", "session_type": "general"}

        apps = [a.name for a in ctx.active_applications]
        titles = [a.window_title or "" for a in ctx.active_applications]
        urls = [t.url for t in ctx.browser_tabs]
        term_out = (ctx.terminals[0].recent_output_preview if ctx.terminals else None) or ""

        session_type = self._classifier.classify(
            apps=apps,
            window_titles=titles,
            terminal_output=term_out,
            browser_urls=urls,
        )
        project = self.detect_primary_project(ctx)

        summary = (
            f"Current workspace appears focused on {project} "
            f"{session_type.value}."
        )
        if session_type == WorkspaceSessionType.DEBUGGING:
            summary = f"Current workspace appears focused on {project} infrastructure debugging."

        return {
            "summary": summary,
            "session_type": session_type.value,
            "primary_project": project,
            "active_repository": ctx.repository_path or self._active_repo,
            "linked_workflows": ctx.active_workflow_ids or self._linked_workflows,
            "active_objectives": self._objectives,
            "clusters": self.cluster_workspace_context(ctx),
            "explainable": {
                "classification_inputs": {"apps": apps[:5], "tab_count": len(urls)},
            },
        }

    def detect_primary_project(self, ctx: UnifiedContextSession) -> str:
        if ctx.repository_path:
            return ctx.repository_path.replace("\\", "/").rstrip("/").split("/")[-1]
        return ctx.project

    def cluster_workspace_context(self, ctx: UnifiedContextSession) -> list[dict[str, Any]]:
        clusters: list[dict[str, Any]] = []
        if ctx.active_applications and ctx.terminals:
            clusters.append({"label": "dev_environment", "members": ["ide", "terminal"]})
        if ctx.browser_tabs and ctx.repository_path:
            clusters.append({"label": "repo_research", "members": ["browser", "repository"]})
        return clusters

    async def emit_summary(self, summary: dict[str, Any]) -> None:
        await self._event_bus.publish(
            Event(
                type=EventType.WORKSPACE_INTELLIGENCE_UPDATED,
                source=AgentId.ODIN,
                payload=summary,
            )
        )
