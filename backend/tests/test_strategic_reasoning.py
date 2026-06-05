"""Strategic reasoning tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.strategic_reasoning.economic_reasoning import balance_resources
from odin_backend.core.strategic_reasoning.geopolitical_reasoning import assess_scenario
from odin_backend.core.strategic_reasoning.recursive_planning import recursive_plan
from odin_backend.core.strategic_reasoning.risk_projection import project_risk
from odin_backend.core.strategic_reasoning.systems_reasoning import analyze_system
from odin_backend.core.streaming.serializers import resolve_channels_for_trace


@pytest.fixture
def settings(tmp_path):
    db = tmp_path / "strat.db"
    return Settings(
        database_url=f"sqlite+aiosqlite:///{db.resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        runtime_enable_background_loops=False,
        strategic_reasoning_enabled=True,
        world_simulation_enabled=True,
        knowledge_fabric_enabled=True,
        federation_enabled=True,
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
async def test_analyze_goal(app):
    r = await app.strategic_reasoning.analyze(goal="optimize_throughput")
    assert r["accepted"] is True
    assert "analysis" in r
    assert "assumptions" in r["analysis"]


@pytest.mark.asyncio
async def test_analyze_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 's.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        strategic_reasoning_enabled=False,
        runtime_enable_background_loops=False,
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    r = await odin.strategic_reasoning.analyze(goal="x")
    assert r["accepted"] is False
    await odin.shutdown()


@pytest.mark.asyncio
async def test_create_objective(app):
    obj = app.strategic_reasoning.create_objective(title="Long horizon", horizon_days=60)
    assert obj["title"] == "Long horizon"


@pytest.mark.asyncio
async def test_strategy_snapshot(app):
    await app.strategic_reasoning.analyze(goal="test")
    snap = app.strategic_reasoning.snapshot()
    assert len(snap["recent_analyses"]) >= 1


def test_recursive_plan_depth():
    plan = recursive_plan("goal", depth=5)
    assert len(plan) == 5


def test_balance_resources():
    r = balance_resources({"cpu": 2.0, "mem": 1.0})
    assert r["balanced"] is True
    assert abs(sum(r["allocation"].values()) - 1.0) < 0.01


def test_project_risk_levels():
    low = project_risk(likelihood=0.1, impact=0.2)
    high = project_risk(likelihood=0.9, impact=0.9)
    assert low["level"] == "low"
    assert high["level"] == "high"


def test_analyze_system():
    s = analyze_system(["a", "b"], [("a", "b")])
    assert s["component_count"] == 2


def test_assess_geopolitical():
    g = assess_scenario("region-a", ["trade", "stability", "resources"])
    assert g["risk_level"] == "moderate"


@pytest.mark.parametrize("goal", ["scale", "optimize", "recover", "plan", "audit"])
@pytest.mark.asyncio
async def test_analyze_goals(app, goal):
    r = await app.strategic_reasoning.analyze(goal=goal)
    assert r["accepted"] is True
    assert r["analysis"]["confidence"] > 0


@pytest.mark.parametrize("depth", [1, 2, 3, 4, 5])
def test_recursive_plan_param(depth):
    assert len(recursive_plan("g", depth=depth)) == depth


@pytest.mark.parametrize("likelihood,impact", [(0.1, 0.1), (0.5, 0.5), (0.8, 0.9)])
def test_risk_scores(likelihood, impact):
    r = project_risk(likelihood=likelihood, impact=impact)
    assert 0 <= r["risk_score"] <= 1


@pytest.mark.parametrize("i", range(15))
@pytest.mark.asyncio
async def test_multiple_analyses(app, i):
    r = await app.strategic_reasoning.analyze(goal=f"goal_{i}")
    assert r["accepted"] is True


def test_strategy_trace_channel():
    ev = TraceEvent(
        kind=TraceEventKind.STRATEGY_GENERATED,
        trace_id="t", span_id="s", causal_chain_id="c", message="strat",
    )
    ch = resolve_channels_for_trace(ev)
    assert "strategy:runtime" in ch


@pytest.mark.asyncio
async def test_analysis_has_knowledge_refs(app):
    r = await app.strategic_reasoning.analyze(goal="with_knowledge")
    assert "knowledge_references" in r["analysis"]


@pytest.mark.asyncio
async def test_geopolitical_assess(app):
    g = app.strategic_reasoning.assess_geopolitical(region="test", factors=["a", "b"])
    assert "assumptions" in g
