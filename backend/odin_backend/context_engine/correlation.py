"""Correlate tabs, files, terminals, workflows into unified sessions."""

from odin_backend.context_engine.sessions import (
    ApplicationContext,
    BrowserTabContext,
    TerminalContext,
    UnifiedContextSession,
)


class ContextCorrelator:
    def correlate(
        self,
        *,
        applications: list[ApplicationContext] | None = None,
        tabs: list[BrowserTabContext] | None = None,
        terminals: list[TerminalContext] | None = None,
        workflow_ids: list[str] | None = None,
        conversation_id: str | None = None,
        project: str = "PROJECT_ODIN",
        repository: str | None = None,
    ) -> UnifiedContextSession:
        session = UnifiedContextSession(
            project=project,
            active_applications=applications or [],
            browser_tabs=tabs or [],
            terminals=terminals or [],
            active_workflow_ids=workflow_ids or [],
            conversation_session_id=conversation_id,
            repository_path=repository,
        )
        session.insight = self._generate_insight(session)
        return session

    def _generate_insight(self, session: UnifiedContextSession) -> str:
        parts: list[str] = []
        apps = {a.name.lower() for a in session.active_applications}
        if "code" in " ".join(apps) or "vscode" in " ".join(apps):
            parts.append("development session")
        if session.browser_tabs:
            parts.append(f"{len(session.browser_tabs)} browser tab(s)")
        if session.terminals:
            parts.append(f"{len(session.terminals)} terminal(s)")
        if session.repository_path:
            parts.append(f"repo: {session.repository_path}")
        if session.active_workflow_ids:
            parts.append(f"{len(session.active_workflow_ids)} active workflow(s)")

        if not parts:
            return f"Ambient context for {session.project} — limited activity detected."

        focus = ", ".join(parts)
        return f"Current activity appears related to {session.project}: {focus}."
