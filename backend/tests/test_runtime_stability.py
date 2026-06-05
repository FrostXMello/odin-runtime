"""Prompt 35 production runtime — runtime stability tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.stability.health_supervisor import HealthSupervisor
from odin_backend.core.stability.state_checkpointing import StateCheckpointing
from odin_backend.core.stability.watchdog_runtime import WatchdogRuntime
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
async def test_app_has_runtime_guardian(app):
    assert hasattr(app, "runtime_guardian")


@pytest.mark.asyncio
async def test_supervise(app):
    r = await app.runtime_guardian.supervise()
    assert r["accepted"] is True
    assert "health" in r
    assert "checkpoint_id" in r


@pytest.mark.asyncio
async def test_recover(app):
    r = await app.runtime_guardian.recover()
    assert r["accepted"] is True
    assert app.runtime_guardian.snapshot()["recoveries"] >= 1


@pytest.mark.asyncio
async def test_emergency(app):
    r = await app.runtime_guardian.emergency()
    assert r["accepted"] is True
    assert "degraded" in r or "crash_recovery" in r


@pytest.mark.asyncio
async def test_checkpoint(app):
    ckpt = await app.runtime_guardian.checkpoint(label="test")
    assert "id" in ckpt
    assert ckpt["label"] == "test"


@pytest.mark.asyncio
async def test_snapshot(app):
    await app.runtime_guardian.supervise()
    snap = app.runtime_guardian.snapshot()
    assert "mode" in snap
    assert "watchdog" in snap
    assert "checkpoints" in snap


@pytest.mark.asyncio
async def test_supervise_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        runtime_guardian_enabled=False,
        runtime_enable_background_loops=False,
        model_provider="mock",
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    r = await odin.runtime_guardian.supervise()
    assert r["accepted"] is False
    assert r["reason"] == "runtime_guardian_disabled"
    await odin.shutdown()


@pytest.mark.asyncio
async def test_recover_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        runtime_guardian_enabled=False,
        runtime_enable_background_loops=False,
        model_provider="mock",
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    r = await odin.runtime_guardian.recover()
    assert r["accepted"] is False
    await odin.shutdown()


@pytest.mark.asyncio
async def test_emergency_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        runtime_guardian_enabled=False,
        runtime_enable_background_loops=False,
        model_provider="mock",
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    r = await odin.runtime_guardian.emergency()
    assert r["accepted"] is False
    await odin.shutdown()


@pytest.mark.asyncio
async def test_connect_heartbeat(app):
    await app.runtime_guardian.connect()
    snap = app.runtime_guardian.snapshot()
    assert "watchdog" in snap


def test_health_supervisor_evaluate_healthy():
    hs = HealthSupervisor()
    report = hs.evaluate(loop_age_s=1.0, memory_pressure="normal", stalled_loops=0)
    assert report["status"] == "healthy"
    assert hs.history(1)[-1]["status"] == "healthy"


def test_health_supervisor_evaluate_degraded():
    hs = HealthSupervisor()
    report = hs.evaluate(loop_age_s=1.0, memory_pressure="critical", stalled_loops=0)
    assert report["status"] == "degraded"


@pytest.mark.parametrize("stalled", [0, 1, 3])
def test_health_supervisor_stalled_loops(stalled):
    hs = HealthSupervisor()
    report = hs.evaluate(loop_age_s=0.5, memory_pressure="normal", stalled_loops=stalled)
    expected = "healthy" if stalled == 0 else "degraded"
    assert report["status"] == expected


def test_watchdog_heartbeat_and_snapshot():
    wd = WatchdogRuntime(stall_threshold_s=120.0)
    wd.heartbeat("test_component")
    snap = wd.snapshot()
    assert "test_component" in snap["heartbeats"]


def test_watchdog_detect_stalled_empty():
    wd = WatchdogRuntime()
    assert wd.detect_stalled() == []


def test_state_checkpointing_create_and_list():
    ck = StateCheckpointing()
    created = ck.create(label="unit", state={"x": 1})
    listed = ck.list_all()
    assert created["id"] in [c["id"] for c in listed]


def test_state_checkpointing_rollback():
    ck = StateCheckpointing()
    created = ck.create(label="rollback", state={"value": 42})
    restored = ck.rollback(created["id"])
    assert restored == {"value": 42}


def test_runtime_recovered_channel():
    ev = TraceEvent(kind=TraceEventKind.RUNTIME_RECOVERED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "stability:runtime" in resolve_channels_for_trace(ev)


def test_degraded_mode_enabled_channel():
    ev = TraceEvent(kind=TraceEventKind.DEGRADED_MODE_ENABLED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "stability:runtime" in resolve_channels_for_trace(ev)


def test_watchdog_triggered_channel():
    ev = TraceEvent(kind=TraceEventKind.WATCHDOG_TRIGGERED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "stability:runtime" in resolve_channels_for_trace(ev)


def test_runtime_repaired_channel():
    ev = TraceEvent(kind=TraceEventKind.RUNTIME_REPAIRED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "stability:runtime" in resolve_channels_for_trace(ev)


@pytest.mark.parametrize("i", range(35))
@pytest.mark.asyncio
async def test_supervise_bulk(app, i):
    r = await app.runtime_guardian.supervise()
    assert r["accepted"] is True
    assert r["health"]["status"] in ("healthy", "degraded")


@pytest.mark.parametrize("i", range(15))
@pytest.mark.asyncio
async def test_checkpoint_bulk(app, i):
    ckpt = await app.runtime_guardian.checkpoint(label=f"bulk-{i}")
    assert ckpt["label"] == f"bulk-{i}"


@pytest.mark.parametrize("i", range(10))
@pytest.mark.asyncio
async def test_recover_bulk(app, i):
    r = await app.runtime_guardian.recover()
    assert r["accepted"] is True


@pytest.mark.parametrize("i", range(8))
@pytest.mark.asyncio
async def test_emergency_bulk(app, i):
    r = await app.runtime_guardian.emergency()
    assert r["accepted"] is True
