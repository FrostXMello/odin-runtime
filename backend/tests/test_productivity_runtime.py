"""Prompt 36 production runtime — productivity and communications tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.productivity.focus_sessions import FocusSessions
from odin_backend.core.productivity.interruption_filter import should_interrupt
from odin_backend.core.productivity.workload_analysis import analyze_workload
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


@pytest.mark.asyncio
async def test_app_has_productivity(app):
    assert hasattr(app, "productivity_runtime")
    assert hasattr(app, "communications_runtime")


@pytest.mark.asyncio
async def test_create_task(app):
    r = await app.productivity_runtime.create_task(title="Write tests", project_id="p1")
    assert r["accepted"] is True
    assert r["task"]["title"] == "Write tests"
    assert r["task"]["status"] == "open"


@pytest.mark.asyncio
async def test_start_focus(app):
    r = await app.productivity_runtime.start_focus(label="deep work")
    assert r["accepted"] is True
    assert r["session"]["label"] == "deep work"


@pytest.mark.asyncio
async def test_stop_focus(app):
    await app.productivity_runtime.start_focus(label="session")
    r = await app.productivity_runtime.stop_focus()
    assert r["accepted"] is True
    assert r["session"] is not None
    assert "ended_at" in r["session"]


@pytest.mark.asyncio
async def test_analytics(app):
    await app.productivity_runtime.create_task(title="task-a")
    analytics = app.productivity_runtime.analytics()
    assert "schedule" in analytics
    assert "workload" in analytics
    assert analytics["workload"]["open"] >= 1


@pytest.mark.asyncio
async def test_snapshot(app):
    await app.productivity_runtime.create_task(title="snap-task")
    snap = app.productivity_runtime.snapshot()
    assert snap["open_tasks"] >= 1
    assert "analytics" in snap


@pytest.mark.asyncio
async def test_briefing(app, tmp_path):
    proj = tmp_path / "brief-proj"
    proj.mkdir()
    await app.project_os.register_project(name="brief", path=str(proj.resolve()))
    await app.productivity_runtime.create_task(title="brief-task")
    r = await app.communications_runtime.briefing()
    assert r["accepted"] is True
    assert "briefing" in r
    assert "summary" in r["briefing"]


@pytest.mark.asyncio
async def test_create_task_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        productivity_enabled=False,
        runtime_enable_background_loops=False,
        model_provider="mock",
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    r = await odin.productivity_runtime.create_task(title="blocked")
    assert r["accepted"] is False
    assert r["reason"] == "productivity_disabled"
    await odin.shutdown()


@pytest.mark.asyncio
async def test_start_focus_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        productivity_enabled=False,
        runtime_enable_background_loops=False,
        model_provider="mock",
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    r = await odin.productivity_runtime.start_focus(label="blocked")
    assert r["accepted"] is False
    await odin.shutdown()


@pytest.mark.asyncio
async def test_briefing_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        communications_enabled=False,
        runtime_enable_background_loops=False,
        model_provider="mock",
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    r = await odin.communications_runtime.briefing()
    assert r["accepted"] is False
    assert r["reason"] == "communications_disabled"
    await odin.shutdown()


def test_focus_sessions_unit():
    fs = FocusSessions()
    started = fs.start(label="unit")
    assert started["label"] == "unit"
    ended = fs.stop()
    assert ended is not None
    assert fs.stop() is None


def test_workload_analysis_normal():
    tasks = [{"status": "open"} for _ in range(5)]
    wl = analyze_workload(tasks)
    assert wl["open"] == 5
    assert wl["load"] == "normal"


def test_workload_analysis_high():
    tasks = [{"status": "open"} for _ in range(12)]
    wl = analyze_workload(tasks)
    assert wl["load"] == "high"


@pytest.mark.parametrize(
    "focus_active,priority,expected",
    [
        (False, "low", True),
        (True, "low", False),
        (True, "urgent", True),
        (True, "critical", True),
    ],
)
def test_interruption_filter(focus_active, priority, expected):
    assert should_interrupt(focus_active=focus_active, priority=priority) is expected


def test_focus_session_started_channel():
    ev = TraceEvent(kind=TraceEventKind.FOCUS_SESSION_STARTED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "productivity:runtime" in resolve_channels_for_trace(ev)


def test_productivity_pattern_detected_channel():
    ev = TraceEvent(kind=TraceEventKind.PRODUCTIVITY_PATTERN_DETECTED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "productivity:runtime" in resolve_channels_for_trace(ev)


@pytest.mark.parametrize("i", range(30))
@pytest.mark.asyncio
async def test_create_task_bulk(app, i):
    r = await app.productivity_runtime.create_task(title=f"task-{i}", project_id=f"p-{i % 5}")
    assert r["accepted"] is True


@pytest.mark.parametrize("i", range(25))
@pytest.mark.asyncio
async def test_focus_cycle_bulk(app, i):
    start = await app.productivity_runtime.start_focus(label=f"focus-{i}")
    assert start["accepted"] is True
    stop = await app.productivity_runtime.stop_focus()
    assert stop["accepted"] is True


@pytest.mark.parametrize("i", range(20))
@pytest.mark.asyncio
async def test_analytics_bulk(app, i):
    await app.productivity_runtime.create_task(title=f"analytics-{i}")
    analytics = app.productivity_runtime.analytics()
    assert analytics["workload"]["total"] >= 1


@pytest.mark.parametrize("i", range(15))
@pytest.mark.asyncio
async def test_snapshot_bulk(app, i):
    await app.productivity_runtime.create_task(title=f"snap-{i}")
    snap = app.productivity_runtime.snapshot()
    assert snap["open_tasks"] >= 1


@pytest.mark.parametrize(
    "label",
    ["coding", "review", "planning", "debug", "docs", "coding", "review", "planning", "debug", "docs"],
)
@pytest.mark.asyncio
async def test_focus_labels(app, label):
    r = await app.productivity_runtime.start_focus(label=label)
    assert r["accepted"] is True
    assert r["session"]["label"] == label
    await app.productivity_runtime.stop_focus()
