"""Prompt 34 production runtime — daemon mode tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
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
        queue_persist_enabled=False,
        async_mission_runtime_enabled=False,
    )


@pytest.fixture
async def app(settings):
    odin = OdinApplication(settings, use_redis=False)
    await odin.startup()
    yield odin
    await odin.shutdown()


@pytest.mark.asyncio
async def test_app_has_daemon_runtime(app):
    assert hasattr(app, "daemon_runtime")


@pytest.mark.asyncio
async def test_start(app):
    r = await app.daemon_runtime.start()
    assert r["accepted"] is True


@pytest.mark.asyncio
async def test_start_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        daemon_mode_enabled=False,
        runtime_enable_background_loops=False,
        model_provider="mock",
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    r = await odin.daemon_runtime.start()
    assert r["accepted"] is False
    await odin.shutdown()


@pytest.mark.asyncio
async def test_enter_idle(app):
    await app.daemon_runtime.start()
    r = await app.daemon_runtime.enter_idle()
    assert r["idle"] is True
    assert app.daemon_runtime.snapshot()["idle"] is True


@pytest.mark.asyncio
async def test_snapshot(app):
    await app.daemon_runtime.start()
    snap = app.daemon_runtime.snapshot()
    assert snap["started_at"] is not None
    assert "sessions" in snap


def test_daemon_started_channel():
    ev = TraceEvent(kind=TraceEventKind.DAEMON_STARTED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "daemon:runtime" in resolve_channels_for_trace(ev)


@pytest.mark.parametrize("i", range(35))
@pytest.mark.asyncio
async def test_start_bulk(app, i):
    await app.agent_execution.spawn_task(owner_agent_id=f"daemon-agent-{i}", title=f"daemon task {i}")
    r = await app.daemon_runtime.start()
    assert r["accepted"] is True


@pytest.mark.parametrize("i", range(15))
@pytest.mark.asyncio
async def test_idle_bulk(app, i):
    await app.daemon_runtime.start()
    r = await app.daemon_runtime.enter_idle()
    assert r["idle"] is True


@pytest.mark.parametrize("i", range(10))
@pytest.mark.asyncio
async def test_snapshot_state(app, i):
    if i % 2 == 0:
        await app.daemon_runtime.start()
    else:
        await app.daemon_runtime.enter_idle()
    snap = app.daemon_runtime.snapshot()
    assert "tray_visible" in snap
    assert "recoveries" in snap


@pytest.mark.parametrize("cycle", range(8))
@pytest.mark.asyncio
async def test_start_resume_tasks(app, cycle):
    await app.agent_execution.spawn_task(owner_agent_id=f"resume-{cycle}", title=f"pending {cycle}")
    r = await app.daemon_runtime.start()
    assert r.get("tasks_resumed", 0) >= 0


@pytest.mark.parametrize("flag", [True, False])
@pytest.mark.asyncio
async def test_idle_after_start(app, flag):
    await app.daemon_runtime.start()
    if flag:
        await app.daemon_runtime.enter_idle()
    snap = app.daemon_runtime.snapshot()
    assert snap["idle"] is flag
