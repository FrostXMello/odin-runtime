"""Developer integrations orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.integrations.cursor_bridge import parse_cursor_context
from odin_backend.core.integrations.filesystem_watchers import detect_changes
from odin_backend.core.integrations.github_runtime import GitHubRuntime
from odin_backend.core.integrations.git_observer import summarize_commits
from odin_backend.core.integrations.repo_activity import RepoActivity
from odin_backend.core.integrations.terminal_memory import TerminalMemory
from odin_backend.core.integrations.vscode_bridge import parse_vscode_context


class IntegrationsRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._github = GitHubRuntime()
        self._activity = RepoActivity()
        self._terminal = TerminalMemory()
        self._watched_files: set[str] = set()

    async def ingest_editor(self, *, editor: str, snapshot: dict[str, Any]) -> dict[str, Any]:
        if not getattr(self._app.settings, "developer_integrations_enabled", False):
            return {"accepted": False, "reason": "developer_integrations_disabled"}
        if editor == "cursor":
            ctx = parse_cursor_context(snapshot)
        else:
            ctx = parse_vscode_context(snapshot)
        repo = snapshot.get("repo", "local")
        self._activity.record(repo=repo, event="editor_active", detail=ctx)
        self._emit("workspace_linked", {"editor": ctx["editor"], "repo": repo})
        return {"accepted": True, "context": ctx}

    async def ingest_git(self, *, repo: str, commits: list[dict[str, Any]]) -> dict[str, Any]:
        if not getattr(self._app.settings, "developer_integrations_enabled", False):
            return {"accepted": False, "reason": "developer_integrations_disabled"}
        summary = summarize_commits(commits)
        self._activity.record(repo=repo, event="git_observed", detail=summary)
        self._emit("repository_indexed", {"repo": repo, "commits": summary["count"]})
        return {"accepted": True, "summary": summary, "write_allowed": False}

    async def ingest_terminal(self, *, session_id: str, line: str) -> dict[str, Any]:
        self._terminal.append(session_id, line)
        return {"accepted": True, "session_id": session_id}

    async def ingest_ide_context(self, *, snapshot: dict[str, Any]) -> dict[str, Any]:
        if not getattr(self._app.settings, "developer_integrations_enabled", False):
            return {"accepted": False, "reason": "developer_integrations_disabled"}
        editor = snapshot.get("editor", "vscode")
        ctx = await self.ingest_editor(editor=editor, snapshot=snapshot)
        branch = snapshot.get("branch", "main")
        tabs = snapshot.get("open_tabs", [])
        diff = snapshot.get("git_diff", "")
        runtime_error = snapshot.get("runtime_error")
        debugging = bool(runtime_error)
        cognition = {
            "branch": branch,
            "open_tabs": len(tabs),
            "diff_lines": len(diff.splitlines()) if diff else 0,
            "debugging_session": debugging,
            "error_correlation": runtime_error is not None,
        }
        if hasattr(self._app, "engineering_memory") and tabs:
            await self._app.engineering_memory.start_session(
                repo=snapshot.get("repo", "local"), focus=tabs[0] if tabs else "unknown"
            )
        return {"accepted": True, "editor": ctx, "cognition": cognition}

    async def watch_files(self, *, paths: list[str]) -> dict[str, Any]:
        after = set(paths)
        changes = detect_changes(before=self._watched_files, after=after)
        self._watched_files = after
        return {"accepted": True, "changes": changes}

    def snapshot(self) -> dict[str, Any]:
        return {
            "github": self._github.snapshot(),
            "activity": self._activity.heatmap(10),
            "terminal_sessions": len(self._terminal._sessions),
        }

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="integrations")
