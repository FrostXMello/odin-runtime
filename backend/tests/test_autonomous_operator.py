"""Autonomous operator mode tests."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.autonomy.autonomy_policy import AutonomyPermissionMode
from odin_backend.core.autonomy.objective_graph import PersistentObjective
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.safety.loop_detection import LoopDetector
from odin_backend.core.safety.throttle import MissionThrottle


@pytest.fixture
def settings(tmp_path):
    db = tmp_path / "auto_op.db"
    return Settings(
        database_url=f"sqlite+aiosqlite:///{db.resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        runtime_enable_background_loops=False,
        conscious_loop_enabled=False,
        cognitive_learning_enabled=False,
        local_cognition_enabled=True,
        model_provider="mock",
        autonomous_operator_enabled=False,
        autonomy_mode="supervised",
        queue_persist_enabled=False,
        async_mission_runtime_enabled=False,
        execution_engine_enabled=True,
    )


@pytest.fixture
async def app(settings):
    odin = OdinApplication(settings, use_redis=False)
    await odin.startup()
    yield odin
    await odin.shutdown()


# --- Objectives ---


@pytest.mark.asyncio
async def test_objective_graph_persistence(app):
    objs = await app.objective_manager.list_all()
    assert len(objs) >= 4


@pytest.mark.asyncio
async def test_create_objective(app):
    obj = await app.objective_manager.create(title="Test objective", priority=0.7)
    assert obj.objective_id
    found = await app.objective_manager.list_all()
    assert any(o.objective_id == obj.objective_id for o in found)


@pytest.mark.asyncio
async def test_objective_reinforce(app):
    obj = await app.objective_manager.create(title="Reinforce test")
    await app.objective_manager.graph.reinforce(obj.objective_id, success=True)
    updated = await app.objective_manager.list_all()
    match = next(o for o in updated if o.objective_id == obj.objective_id)
    assert match.confidence >= 0.5


# --- Autonomy loop ---


@pytest.mark.asyncio
async def test_autonomy_start_pause(app):
    snap = await app.autonomous_loop.start()
    assert snap["run_state"] == "running"
    paused = await app.autonomous_loop.pause()
    assert paused["run_state"] == "paused"
    await app.autonomous_loop.stop()


@pytest.mark.asyncio
async def test_autonomy_snapshot(app):
    snap = app.autonomous_loop.snapshot()
    assert "state" in snap
    assert "metrics" in snap


@pytest.mark.asyncio
async def test_initiative_engine(app):
    initiatives = await app.autonomous_loop._initiative.propose_initiatives()
    assert initiatives


# --- Safety ---


def test_mission_throttle():
    t = MissionThrottle(max_per_hour=2)
    assert t.allow()
    t.record()
    t.record()
    assert not t.allow()


def test_loop_detector_runaway():
    d = LoopDetector(window_seconds=60.0)
    for _ in range(16):
        d.record()
    assert d.is_runaway()


@pytest.mark.asyncio
async def test_safety_observe_only_blocks_missions(app):
    app.settings.autonomy_mode = AutonomyPermissionMode.OBSERVE_ONLY.value
    assert not app.autonomy_safety.allow_mission_spawn()


@pytest.mark.asyncio
async def test_safety_violations_snapshot(app):
    app.autonomy_safety._intervene("mission_throttle", {"reason": "test"})
    snap = app.autonomy_safety.snapshot()
    assert snap["interventions"]


# --- Environment ---


@pytest.mark.asyncio
async def test_environment_alerts(app):
    alerts = await app.environment_monitor.collect_alerts()
    assert isinstance(alerts, list)


# --- Research ---


@pytest.mark.asyncio
async def test_research_session(app):
    session = await app.research_engine.start(topic="planner accuracy")
    assert session.session_id
    assert session.iterations


@pytest.mark.asyncio
async def test_research_iteration(app):
    result = await app.research_engine.run_iteration(topic="routing latency")
    assert result["hypothesis"]


# --- Identity ---


@pytest.mark.asyncio
async def test_identity_persistence(app):
    state = app.identity_store.state
    assert state.name == "Odin"


@pytest.mark.asyncio
async def test_identity_bounded_update(app):
    before = app.identity_store.state.behavioral.verbosity
    await app.identity_store.update({"behavioral": {"verbosity": before + 0.5}})
    after = app.identity_store.state.behavioral.verbosity
    assert abs(after - before) <= 0.15 + 1e-6
    assert after <= 0.9


# --- APIs ---


@pytest.mark.asyncio
async def test_autonomy_api(app):
    from odin_backend.api.routes import autonomy_runtime

    api = FastAPI()
    api.state.odin = app
    api.include_router(autonomy_runtime.router, prefix="/api/v1")
    transport = ASGITransport(app=api)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/api/v1/runtime/autonomy")
        assert r.status_code == 200
        r2 = await client.get("/api/v1/runtime/objectives")
        assert r2.status_code == 200
        r3 = await client.get("/api/v1/runtime/safety")
        assert r3.status_code == 200


@pytest.mark.asyncio
async def test_stream_channels_autonomy():
    from odin_backend.core.streaming.serializers import resolve_channels_for_trace

    ev = TraceEvent(
        kind=TraceEventKind.AUTONOMY_CYCLE_STARTED,
        trace_id="t",
        span_id="s",
        causal_chain_id="c",
    )
    ch = resolve_channels_for_trace(ev)
    assert "autonomy:runtime" in ch


@pytest.mark.asyncio
async def test_app_has_autonomous_services(app):
    assert hasattr(app, "autonomous_loop")
    assert hasattr(app, "objective_manager")
    assert hasattr(app, "environment_monitor")
    assert hasattr(app, "research_engine")
    assert hasattr(app, "identity_store")
    assert hasattr(app, "autonomy_safety")
