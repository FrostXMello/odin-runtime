"""Contextual action generator and workflow suggestions."""

from typing import Any

from odin_backend.context_engine.sessions import UnifiedContextSession
from odin_backend.workspace_intelligence.classifier import WorkspaceSessionType
class ContextualActionGenerator:
    def generate_actions(
        self,
        ctx: UnifiedContextSession | None,
        ws_summary: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        actions: list[dict[str, str]] = [
            {"id": "ask", "label": "Ask ODIN", "prompt": "", "category": "general"},
        ]
        suggestions: list[dict[str, str]] = []
        app_name = ""
        session_type = WorkspaceSessionType.GENERAL

        if ctx and ctx.active_applications:
            app_name = ctx.active_applications[0].name.lower()
        if ws_summary:
            session_type = WorkspaceSessionType(ws_summary.get("session_type", "general"))

        if "code" in app_name or session_type == WorkspaceSessionType.CODING:
            actions.extend([
                {"id": "repo_sum", "label": "Summarize repository", "prompt": "summarize this repository structure and purpose", "category": "vscode"},
                {"id": "arch", "label": "Explain architecture", "prompt": "explain the architecture of the current project", "category": "vscode"},
                {"id": "errors", "label": "Inspect errors", "prompt": "inspect and explain recent errors in the workspace", "category": "vscode"},
                {"id": "logs", "label": "Analyze logs", "prompt": "analyze recent logs for issues", "category": "vscode"},
                {"id": "stack", "label": "Explain stack trace", "prompt": "explain the latest stack trace", "category": "vscode"},
            ])
            suggestions.append({
                "id": "wf_continue",
                "message": "Continue unresolved coding workflow?",
                "reason": "Active development session detected",
            })

        if session_type == WorkspaceSessionType.DEBUGGING:
            actions.extend([
                {"id": "debug", "label": "Debug assistance", "prompt": "help debug the current failure", "category": "vscode"},
            ])

        if ctx and ctx.browser_tabs or "chrome" in app_name:
            actions.extend([
                {"id": "research", "label": "Summarize research", "prompt": "summarize and cluster my research tabs", "category": "browser"},
                {"id": "compare", "label": "Compare frameworks", "prompt": "compare the frameworks in my open tabs", "category": "browser"},
                {"id": "notes", "label": "Extract notes", "prompt": "extract structured notes from research tabs", "category": "browser"},
                {"id": "save_session", "label": "Save research session", "prompt": "save this research session to memory", "category": "browser"},
            ])

        if ctx and ctx.terminals or session_type == WorkspaceSessionType.DEPLOYMENT:
            actions.extend([
                {"id": "term_fail", "label": "Explain failure", "prompt": "explain the terminal failure output", "category": "terminal"},
                {"id": "term_logs", "label": "Summarize logs", "prompt": "summarize terminal log output", "category": "terminal"},
                {"id": "term_fix", "label": "Suggest fixes", "prompt": "suggest fixes for the terminal error", "category": "terminal"},
                {"id": "infra", "label": "Detect infra issues", "prompt": "detect infrastructure issues from terminal output", "category": "terminal"},
            ])

        return {
            "actions": actions,
            "workflow_suggestions": suggestions,
            "explainable": {
                "application": app_name,
                "session_type": session_type.value,
                "action_count": len(actions),
                "requires_approval": True,
            },
        }
