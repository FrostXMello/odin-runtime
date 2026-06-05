"""Prompt 35 production runtime — daemon persistence tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.daemon.adaptive_polling import poll_interval
from odin_backend.core.daemon.daemon_memory_compaction import compact_daemon_state
from odin_backend.core.daemon.heartbeat_persistence import HeartbeatPersistence
from odin_backend.core.daemon.idle_sleep_scheduler import should_wake, sleep_interval
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
async def test_restore_session(app):
    r = await app.daemon_runtime.restore_session()
    assert r["restored"] is True
    assert r["recoveries"] >= 1


@pytest.mark.asyncio
async def test_restore_session_disabled(tmp_path):
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
    r = await odin.daemon_runtime.restore_session()
    assert r["restored"] is False
    await odin.shutdown()


@pytest.mark.asyncio
async def test_tick(app):
    await app.daemon_runtime.start()
    r = await app.daemon_runtime.tick(activity_score=0.0)
    assert "uptime_s" in r
    assert "poll_s" in r
    assert r["uptime_s"] > 0


@pytest.mark.asyncio
async def test_tick_wake_from_idle(app):
    await app.daemon_runtime.start()
    await app.daemon_runtime.enter_idle()
    r = await app.daemon_runtime.tick(activity_score=0.9)
    assert r["idle"] is False


@pytest.mark.asyncio
async def test_idle_with_compaction(app):
    await app.daemon_runtime.start()
    r = await app.daemon_runtime.enter_idle()
    assert r["idle"] is True
    assert "compaction" in r
    assert "remaining" in r["compaction"]


@pytest.mark.asyncio
async def test_heartbeat_in_snapshot(app):
    await app.daemon_runtime.start()
    await app.daemon_runtime.tick()
    snap = app.daemon_runtime.snapshot()
    assert "heartbeat" in snap
    assert snap["heartbeat"]["count"] >= 1


@pytest.mark.asyncio
async def test_snapshot_fields(app):
    await app.daemon_runtime.start()
    snap = app.daemon_runtime.snapshot()
    assert "started_at" in snap
    assert "recoveries" in snap
    assert "uptime_s" in snap


def test_heartbeat_persistence_unit():
    hb = HeartbeatPersistence()
    entry = hb.beat(component="daemon", uptime_s=10.0)
    snap = hb.snapshot()
    assert entry["component"] == "daemon"
    assert snap["count"] == 1
    assert snap["last"] is not None


def test_compact_daemon_state_unit():
    result = compact_daemon_state(cache_entries=250, max_entries=200)
    assert result["evicted"] == 50
    assert result["remaining"] == 200


@pytest.mark.parametrize("pressure,idle,expected_min", [("normal", False, 5.0), ("high", False, 10.0), ("critical", False, 60.0), ("normal", True, 20.0)])
def test_poll_interval_unit(pressure, idle, expected_min):
    assert poll_interval(pressure=pressure, idle=idle) >= expected_min


@pytest.mark.parametrize("idle,on_battery,expected", [(True, True, 30.0), (True, False, 15.0), (False, False, 5.0)])
def test_sleep_interval_unit(idle, on_battery, expected):
    assert sleep_interval(idle=idle, on_battery=on_battery) == expected


@pytest.mark.parametrize("score,expected", [(0.1, False), (0.5, True), (1.0, True)])
def test_should_wake_unit(score, expected):
    assert should_wake(activity_score=score) is expected


def test_daemon_restored_channel():
    ev = TraceEvent(kind=TraceEventKind.DAEMON_RESTORED, trace_id="t", span_id="s", causal_chain_id="c")
    channels = resolve_channels_for_trace(ev)
    assert "daemon:runtime" in channels
    assert "recovery:runtime" in channels


@pytest.mark.parametrize("i", range(35))
@pytest.mark.asyncio
async def test_tick_bulk(app, i):
    await app.daemon_runtime.start()
    if i % 2 == 0:
        await app.daemon_runtime.enter_idle()
    r = await app.daemon_runtime.tick(activity_score=float(i % 10) / 10.0)
    assert r["poll_s"] > 0


@pytest.mark.parametrize("i", range(15))
@pytest.mark.asyncio
async def test_restore_session_bulk(app, i):
    r = await app.daemon_runtime.restore_session()
    assert r["restored"] is True
    assert r["recoveries"] >= 1


@pytest.mark.parametrize("i", range(10))
@pytest.mark.asyncio
async def test_idle_compaction_bulk(app, i):
    await app.daemon_runtime.start()
    r = await app.daemon_runtime.enter_idle()
    assert r["compaction"]["remaining"] >= 0


@pytest.mark.parametrize("i", range(8))
@pytest.mark.asyncio
async def test_heartbeat_persistence_bulk(app, i):
    await app.daemon_runtime.start()
    for _ in range(i + 1):
        await app.daemon_runtime.tick()
    snap = app.daemon_runtime.snapshot()
    assert snap["heartbeat"]["count"] >= i + 1
