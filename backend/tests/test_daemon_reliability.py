"""Prompt 37 production runtime — daemon reliability tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.daemon.daemon_supervisor import MODES, mode_config
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
        deployment_enabled=True,
        performance_enabled=True,
        privacy_enabled=True,
        operator_shell_enabled=True,
        daily_driver_enabled=True,
        local_ai_mode="balanced",
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
async def test_set_mode_valid(app):
    r = await app.daemon_runtime.set_mode("overnight_cognition")
    assert r["accepted"] is True
    assert r["mode"] == "overnight_cognition"
    assert "config" in r


@pytest.mark.asyncio
async def test_set_mode_invalid(app):
    r = await app.daemon_runtime.set_mode("nonexistent_mode")
    assert r["accepted"] is False
    assert r["reason"] == "invalid_mode"


@pytest.mark.asyncio
async def test_watchdog_restart(app):
    r = await app.daemon_runtime.watchdog_restart()
    assert r["accepted"] is True
    assert r["restarts"] >= 1


@pytest.mark.asyncio
async def test_graceful_shutdown(app):
    r = await app.daemon_runtime.graceful_shutdown()
    assert r["accepted"] is True
    assert r["shutdown"] is True


@pytest.mark.asyncio
async def test_record_memory_sample(app):
    r = app.daemon_runtime.record_memory_sample(512)
    assert r["mb"] == 512
    assert "leak_suspected" in r


@pytest.mark.asyncio
async def test_daemon_snapshot(app):
    await app.daemon_runtime.start()
    snap = app.daemon_runtime.snapshot()
    assert "mode" in snap
    assert "restarts" in snap
    assert "heartbeat" in snap


@pytest.mark.parametrize("mode", MODES)
def test_mode_config(mode):
    cfg = mode_config(mode)
    assert "cognition_depth" in cfg


def test_daemon_started_channel():
    ev = TraceEvent(
        kind=TraceEventKind.DAEMON_STARTED,
        trace_id="t",
        span_id="s",
        causal_chain_id="c",
    )
    assert "daemon:runtime" in resolve_channels_for_trace(ev)


def test_daemon_restarted_channel():
    ev = TraceEvent(
        kind=TraceEventKind.DAEMON_RESTARTED,
        trace_id="t",
        span_id="s",
        causal_chain_id="c",
    )
    channels = resolve_channels_for_trace(ev)
    assert "diagnostics:runtime" in channels


def test_daemon_restored_channel():
    ev = TraceEvent(
        kind=TraceEventKind.DAEMON_RESTORED,
        trace_id="t",
        span_id="s",
        causal_chain_id="c",
    )
    channels = resolve_channels_for_trace(ev)
    assert "daemon:runtime" in channels
    assert "recovery:runtime" in channels


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("i", range(30))
@pytest.mark.asyncio
async def test_set_mode_matrix(app, mode, i):
    r = await app.daemon_runtime.set_mode(mode)
    assert r["accepted"] is True
    assert app.daemon_runtime.snapshot()["mode"] == mode


@pytest.mark.parametrize("i", range(40))
@pytest.mark.asyncio
async def test_watchdog_restart_bulk(app, i):
    for _ in range(i + 1):
        r = await app.daemon_runtime.watchdog_restart()
    assert r["accepted"] is True
    assert r["restarts"] == i + 1


@pytest.mark.parametrize("mb", [256, 512, 1024, 2048, 4096])
@pytest.mark.parametrize("i", range(8))
@pytest.mark.asyncio
async def test_memory_sample_matrix(app, mb, i):
    sample = app.daemon_runtime.record_memory_sample(mb + i)
    assert sample["mb"] == mb + i


@pytest.mark.parametrize("i", range(35))
@pytest.mark.asyncio
async def test_graceful_shutdown_bulk(app, i):
    await app.daemon_runtime.start()
    r = await app.daemon_runtime.graceful_shutdown()
    assert r["accepted"] is True


@pytest.mark.parametrize("activity", [0.0, 0.3, 0.7, 1.0])
@pytest.mark.parametrize("i", range(10))
@pytest.mark.asyncio
async def test_tick_activity(app, activity, i):
    await app.daemon_runtime.start()
    r = await app.daemon_runtime.tick(activity_score=activity)
    assert "uptime_s" in r
    assert "poll_s" in r


@pytest.mark.parametrize("i", range(25))
@pytest.mark.asyncio
async def test_idle_cycle(app, i):
    await app.daemon_runtime.start()
    await app.daemon_runtime.enter_idle()
    snap = app.daemon_runtime.snapshot()
    assert snap["idle"] is True
