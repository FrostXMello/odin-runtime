"""Prompt 36 production runtime — project OS tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.project_os.continuity_engine import restore_context
from odin_backend.core.project_os.project_registry import ProjectRegistry
from odin_backend.core.project_os.workflow_patterns import detect_patterns
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


@pytest.fixture
def project_dir(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    (root / "src").mkdir()
    (root / "main.py").write_text("print('hello')\n", encoding="utf-8")
    return root


async def _register(app, project_dir, *, name: str = "odin-test", metadata: dict | None = None):
    return await app.project_os.register_project(
        name=name,
        path=str(project_dir.resolve()),
        metadata=metadata,
    )


@pytest.mark.asyncio
async def test_app_has_project_os(app):
    assert hasattr(app, "project_os")


@pytest.mark.asyncio
async def test_register_project(app, project_dir):
    r = await _register(app, project_dir)
    assert r["accepted"] is True
    assert "project" in r
    assert r["project"]["name"] == "odin-test"
    assert "index" in r
    assert "codebase" in r


@pytest.mark.asyncio
async def test_restore(app, project_dir):
    reg = await _register(app, project_dir, name="restore-me")
    pid = reg["project"]["id"]
    r = await app.project_os.restore(pid, session_id="sess-1")
    assert r["accepted"] is True
    assert r["project_id"] == pid
    assert "summary" in r


@pytest.mark.asyncio
async def test_summarize(app, project_dir):
    reg = await _register(app, project_dir, name="summarize-me")
    pid = reg["project"]["id"]
    r = await app.project_os.summarize(pid)
    assert "project" in r
    assert "repo" in r
    assert "patterns" in r


@pytest.mark.asyncio
async def test_snapshot(app, project_dir):
    await _register(app, project_dir)
    snap = app.project_os.snapshot()
    assert "projects" in snap
    assert snap["projects"] >= 1
    assert "project_list" in snap


@pytest.mark.asyncio
async def test_register_disabled(tmp_path, project_dir):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        project_os_enabled=False,
        runtime_enable_background_loops=False,
        model_provider="mock",
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    r = await odin.project_os.register_project(name="x", path=str(project_dir))
    assert r["accepted"] is False
    assert r["reason"] == "project_os_disabled"
    await odin.shutdown()


@pytest.mark.asyncio
async def test_restore_disabled(tmp_path, project_dir):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        project_os_enabled=False,
        runtime_enable_background_loops=False,
        model_provider="mock",
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    r = await odin.project_os.restore("missing-id")
    assert r["accepted"] is False
    assert r["reason"] == "project_os_disabled"
    await odin.shutdown()


@pytest.mark.asyncio
async def test_restore_not_found(app):
    r = await app.project_os.restore("nonexistent-project-id")
    assert r["accepted"] is False
    assert r["reason"] == "project_not_found"


def test_project_registry_register_get_list():
    reg = ProjectRegistry()
    entry = reg.register(name="alpha", path="/tmp/alpha", metadata={"team": "core"})
    assert entry["name"] == "alpha"
    assert reg.get(entry["id"]) == entry
    assert len(reg.list_all()) == 1


def test_project_registry_multiple():
    reg = ProjectRegistry()
    for i in range(5):
        reg.register(name=f"p{i}", path=f"/tmp/p{i}")
    assert len(reg.list_all()) == 5


@pytest.mark.parametrize(
    "events,expected_kind",
    [
        ([{"kind": "register"}], "register:1"),
        ([{"kind": "register"}, {"kind": "register"}], "register:2"),
        ([{"kind": "edit"}, {"kind": "test"}], "edit:1"),
        ([], ""),
    ],
)
def test_detect_patterns(events, expected_kind):
    patterns = detect_patterns(events)
    if not expected_kind:
        assert patterns == []
    else:
        assert patterns[0] == expected_kind


def test_restore_context_unit():
    project = {"id": "p1", "name": "Odin"}
    timeline = [{"kind": "register"}, {"kind": "edit"}]
    ctx = restore_context(project=project, timeline=timeline)
    assert ctx["project_id"] == "p1"
    assert "Odin" in ctx["summary"]
    assert len(ctx["last_events"]) == 2


def test_project_context_restored_channel():
    ev = TraceEvent(kind=TraceEventKind.PROJECT_CONTEXT_RESTORED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "projects:runtime" in resolve_channels_for_trace(ev)


def test_coding_session_resumed_channel():
    ev = TraceEvent(kind=TraceEventKind.CODING_SESSION_RESUMED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "projects:runtime" in resolve_channels_for_trace(ev)


def test_repository_indexed_channel():
    ev = TraceEvent(kind=TraceEventKind.REPOSITORY_INDEXED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "repositories:runtime" in resolve_channels_for_trace(ev)


@pytest.mark.parametrize("i", range(35))
@pytest.mark.asyncio
async def test_register_bulk(app, project_dir, i):
    r = await _register(app, project_dir, name=f"bulk-proj-{i}")
    assert r["accepted"] is True
    assert r["project"]["name"] == f"bulk-proj-{i}"


@pytest.mark.parametrize("i", range(25))
@pytest.mark.asyncio
async def test_restore_bulk(app, project_dir, i):
    reg = await _register(app, project_dir, name=f"restore-bulk-{i}")
    r = await app.project_os.restore(reg["project"]["id"], session_id=f"sess-{i}")
    assert r["accepted"] is True
    assert r["project_id"] == reg["project"]["id"]


@pytest.mark.parametrize("i", range(15))
@pytest.mark.asyncio
async def test_summarize_bulk(app, project_dir, i):
    reg = await _register(app, project_dir, name=f"sum-{i}")
    r = await app.project_os.summarize(reg["project"]["id"])
    assert r["project"]["name"] == f"sum-{i}"


@pytest.mark.parametrize("i", range(10))
@pytest.mark.asyncio
async def test_snapshot_bulk(app, project_dir, i):
    await _register(app, project_dir, name=f"snap-{i}")
    snap = app.project_os.snapshot()
    assert snap["projects"] >= 1


@pytest.mark.parametrize(
    "name",
    ["frontend", "backend", "infra", "docs", "mobile", "api", "cli", "lib", "core", "tools"],
)
@pytest.mark.asyncio
async def test_register_named_projects(app, project_dir, name):
    r = await _register(app, project_dir, name=name, metadata={"layer": name})
    assert r["accepted"] is True
    assert r["project"]["metadata"]["layer"] == name
