"""Prompt 36 production runtime — developer integrations tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.integrations.filesystem_watchers import detect_changes
from odin_backend.core.integrations.git_observer import summarize_commits
from odin_backend.core.integrations.vscode_bridge import parse_vscode_context
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.streaming.serializers import resolve_channels_for_trace


@pytest.fixture
def settings(tmp_path):
    db = tmp_path / "prod.db"
    return Settings(
        database_url=f"sqlite+aiosqlite:///{db.resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        runtime_enable_background_loops=False,
        conscious_loop_enabled=False,
        model_provider="mock",
        local_cognition_enabled=True,
        local_ai_enabled=True,
        vector_memory_enabled=True,
        agent_execution_enabled=True,
        agent_society_enabled=True,
        copilot_production_enabled=True,
        realtime_voice_enabled=True,
        evaluation_enabled=True,
        resource_optimization_enabled=True,
        daemon_mode_enabled=True,
        runtime_guardian_enabled=True,
        self_healing_enabled=True,
        real_automation_enabled=True,
        memory_consolidation_enabled=True,
        survival_mode="balanced",
        queue_persist_enabled=False,
        async_mission_runtime_enabled=False,
        project_os_enabled=True,
        developer_integrations_enabled=True,
        workspace_knowledge_enabled=True,
        productivity_enabled=True,
        local_search_enabled=True,
        communications_enabled=True,
        storage_optimization_enabled=True,
    )


@pytest.fixture
async def app(settings):
    odin = OdinApplication(settings, use_redis=False)
    await odin.startup()
    yield odin
    await odin.shutdown()


def _editor_snapshot(*, editor: str = "vscode", repo: str = "odin") -> dict:
    return {
        "active_file": "main.py",
        "workspace_folders": ["/workspace/odin"],
        "language": "python",
        "repo": repo,
        "agent_mode": editor == "cursor",
    }


@pytest.mark.asyncio
async def test_app_has_integrations(app):
    assert hasattr(app, "integrations_runtime")


@pytest.mark.asyncio
async def test_ingest_editor_vscode(app):
    r = await app.integrations_runtime.ingest_editor(editor="vscode", snapshot=_editor_snapshot())
    assert r["accepted"] is True
    assert r["context"]["editor"] == "vscode"


@pytest.mark.asyncio
async def test_ingest_editor_cursor(app):
    r = await app.integrations_runtime.ingest_editor(editor="cursor", snapshot=_editor_snapshot(editor="cursor"))
    assert r["accepted"] is True
    assert r["context"]["editor"] == "cursor"


@pytest.mark.asyncio
async def test_ingest_git(app):
    commits = [{"message": "feat: add integrations"}, {"message": "fix: bridge parsing"}]
    r = await app.integrations_runtime.ingest_git(repo="odin", commits=commits)
    assert r["accepted"] is True
    assert r["summary"]["count"] == 2
    assert r["write_allowed"] is False


@pytest.mark.asyncio
async def test_ingest_terminal(app):
    r = await app.integrations_runtime.ingest_terminal(session_id="term-1", line="pytest -q")
    assert r["accepted"] is True
    assert r["session_id"] == "term-1"


@pytest.mark.asyncio
async def test_watch_files(app):
    r = await app.integrations_runtime.watch_files(paths=["/a.py", "/b.py"])
    assert r["accepted"] is True
    assert "changes" in r


@pytest.mark.asyncio
async def test_snapshot(app):
    await app.integrations_runtime.ingest_terminal(session_id="s1", line="ls")
    snap = app.integrations_runtime.snapshot()
    assert "github" in snap
    assert "activity" in snap
    assert snap["terminal_sessions"] >= 1


@pytest.mark.asyncio
async def test_ingest_editor_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        developer_integrations_enabled=False,
        runtime_enable_background_loops=False,
        model_provider="mock",
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    r = await odin.integrations_runtime.ingest_editor(editor="vscode", snapshot=_editor_snapshot())
    assert r["accepted"] is False
    assert r["reason"] == "developer_integrations_disabled"
    await odin.shutdown()


@pytest.mark.asyncio
async def test_ingest_git_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        developer_integrations_enabled=False,
        runtime_enable_background_loops=False,
        model_provider="mock",
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    r = await odin.integrations_runtime.ingest_git(repo="odin", commits=[])
    assert r["accepted"] is False
    await odin.shutdown()


def test_vscode_bridge_unit():
    ctx = parse_vscode_context({"active_file": "app.py", "language": "python", "workspace_folders": ["/w"]})
    assert ctx["editor"] == "vscode"
    assert ctx["active_file"] == "app.py"
    assert ctx["language"] == "python"


def test_git_observer_unit():
    summary = summarize_commits([{"message": "initial commit"}, {"message": "second"}])
    assert summary["count"] == 2
    assert len(summary["messages"]) == 2
    assert summary["write_allowed"] is False


def test_detect_changes_added():
    changes = detect_changes(before=set(), after={"a.py", "b.py"})
    assert set(changes["added"]) == {"a.py", "b.py"}
    assert changes["removed"] == []
    assert changes["changed_count"] == 2


def test_detect_changes_removed():
    changes = detect_changes(before={"old.py"}, after=set())
    assert changes["added"] == []
    assert changes["removed"] == ["old.py"]


def test_detect_changes_unchanged():
    paths = {"main.py"}
    changes = detect_changes(before=paths, after=paths)
    assert changes["changed_count"] == 0


def test_workspace_linked_channel():
    ev = TraceEvent(kind=TraceEventKind.WORKSPACE_LINKED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "workspace:runtime" in resolve_channels_for_trace(ev)


@pytest.mark.parametrize("i", range(30))
@pytest.mark.asyncio
async def test_ingest_editor_bulk(app, i):
    r = await app.integrations_runtime.ingest_editor(
        editor="vscode" if i % 2 == 0 else "cursor",
        snapshot=_editor_snapshot(repo=f"repo-{i}"),
    )
    assert r["accepted"] is True


@pytest.mark.parametrize("i", range(25))
@pytest.mark.asyncio
async def test_ingest_git_bulk(app, i):
    commits = [{"message": f"commit-{i}-{j}"} for j in range(3)]
    r = await app.integrations_runtime.ingest_git(repo=f"bulk-{i}", commits=commits)
    assert r["accepted"] is True
    assert r["summary"]["count"] == 3


@pytest.mark.parametrize("i", range(20))
@pytest.mark.asyncio
async def test_ingest_terminal_bulk(app, i):
    r = await app.integrations_runtime.ingest_terminal(session_id=f"term-{i}", line=f"cmd-{i}")
    assert r["accepted"] is True


@pytest.mark.parametrize("i", range(15))
@pytest.mark.asyncio
async def test_watch_files_bulk(app, i):
    paths = [f"/file-{i}.py", f"/file-{i + 1}.py"]
    r = await app.integrations_runtime.watch_files(paths=paths)
    assert r["accepted"] is True


@pytest.mark.parametrize(
    "editor",
    ["vscode", "cursor", "vscode", "cursor", "vscode", "cursor", "vscode", "cursor", "vscode", "cursor"],
)
@pytest.mark.asyncio
async def test_ingest_editors(app, editor):
    r = await app.integrations_runtime.ingest_editor(editor=editor, snapshot=_editor_snapshot(editor=editor))
    assert r["accepted"] is True
    assert r["context"]["editor"] == editor
