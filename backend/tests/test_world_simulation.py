"""World simulation tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.streaming.serializers import resolve_channels_for_trace
from odin_backend.core.world_simulation.scenario_planner import plan_scenarios
from odin_backend.core.world_simulation.simulation_engine import SimulationEngine
from odin_backend.core.world_simulation.temporal_reasoning import analyze_timeline
from odin_backend.core.world_simulation.uncertainty_engine import quantify_uncertainty


@pytest.fixture
def settings(tmp_path):
    db = tmp_path / "world.db"
    return Settings(
        database_url=f"sqlite+aiosqlite:///{db.resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        runtime_enable_background_loops=False,
        world_simulation_enabled=True,
        federation_enabled=True,
        strategic_reasoning_enabled=True,
        knowledge_fabric_enabled=True,
        model_provider="mock",
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
async def test_upsert_entity(app):
    e = await app.world_simulation.upsert_entity(name="runtime", kind="system", confidence=0.8)
    assert e["name"] == "runtime"


@pytest.mark.asyncio
async def test_project_simulation(app):
    r = await app.world_simulation.project(scenario="deploy", assumptions=["stable"], branches=3)
    assert r["accepted"] is True
    assert len(r["simulation"]["branches"]) == 3


@pytest.mark.asyncio
async def test_project_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'w.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        world_simulation_enabled=False,
        runtime_enable_background_loops=False,
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    r = await odin.world_simulation.project(scenario="x")
    assert r["accepted"] is False
    await odin.shutdown()


@pytest.mark.asyncio
async def test_predict(app):
    p = await app.world_simulation.predict(entity="mission", hypothesis="will succeed", confidence=0.7)
    assert "uncertainty" in p


@pytest.mark.asyncio
async def test_world_snapshot(app):
    await app.world_simulation.upsert_entity(name="a", kind="agent")
    snap = await app.world_simulation.snapshot()
    assert len(snap["entities"]) >= 1


@pytest.mark.asyncio
async def test_causal_link(app):
    link = app.world_simulation.add_causal_link(cause="load", effect="latency", strength=0.6)
    assert link["strength"] == 0.6


@pytest.mark.asyncio
async def test_analyze_strategy(app):
    await app.world_simulation.upsert_entity(name="sys", kind="infra", confidence=0.75)
    result = await app.world_simulation.analyze_strategy(goal="scale")
    assert "projection" in result


def test_simulation_bounded_branches():
    eng = SimulationEngine()
    run = eng.run(scenario="test", assumptions=[], branches=10)
    assert len(run["branches"]) <= 5
    assert run["bounded"] is True
    assert run["reversible"] is True


def test_plan_scenarios():
    steps = plan_scenarios("optimize", horizon_steps=5)
    assert len(steps) == 5


def test_analyze_timeline_improving():
    events = [{"confidence": 0.5}, {"confidence": 0.8}]
    t = analyze_timeline(events)
    assert t["trend"] == "improving"


def test_quantify_uncertainty():
    u = quantify_uncertainty(confidence=0.7, evidence_count=3)
    assert u["uncertainty"] < 0.6
    assert u["confidence"] > 0.4


@pytest.mark.parametrize("i", range(20))
@pytest.mark.asyncio
async def test_entity_persistence(app, i):
    e = await app.world_simulation.upsert_entity(name=f"entity_{i}", kind="test")
    assert "entity_id" in e


@pytest.mark.parametrize("branches", [1, 2, 3, 4, 5])
@pytest.mark.asyncio
async def test_simulation_branches(app, branches):
    r = await app.world_simulation.project(scenario="branch_test", branches=branches)
    assert r["accepted"] is True


@pytest.mark.parametrize("conf", [0.3, 0.5, 0.7, 0.9])
@pytest.mark.asyncio
async def test_prediction_confidence(app, conf):
    p = await app.world_simulation.predict(entity="e", hypothesis="h", confidence=conf)
    assert p["confidence"] == conf


def test_simulation_trace_channel():
    ev = TraceEvent(
        kind=TraceEventKind.SIMULATION_PROJECTED,
        trace_id="t", span_id="s", causal_chain_id="c", message="sim",
    )
    ch = resolve_channels_for_trace(ev)
    assert "simulation:runtime" in ch
    assert "world:runtime" in ch


def test_world_state_trace_channel():
    ev = TraceEvent(
        kind=TraceEventKind.WORLD_STATE_CHANGED,
        trace_id="t", span_id="s", causal_chain_id="c", message="world",
    )
    ch = resolve_channels_for_trace(ev)
    assert "world:runtime" in ch


@pytest.mark.parametrize("scenario", ["deploy", "rollback", "scale", "recover"])
@pytest.mark.asyncio
async def test_scenarios(app, scenario):
    r = await app.world_simulation.project(scenario=scenario)
    assert r["accepted"] is True


@pytest.mark.asyncio
async def test_list_simulations(app):
    await app.world_simulation.project(scenario="s1")
    await app.world_simulation.project(scenario="s2")
    sims = app.world_simulation.list_simulations()
    assert len(sims) >= 2


@pytest.mark.asyncio
async def test_mission_predictions(app):
    p = await app.world_simulation.predict(entity="m", hypothesis="ok", mission_id="mission-1")
    found = app.world_simulation.predictions_for_mission("mission-1")
    assert len(found) >= 1
