"""Operational planning + operator relationship + distributed optimization tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.distributed_optimization.topology_optimizer import optimize_topology
from odin_backend.core.distributed_optimization.workload_balancer import balance
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.operational_planning.strategic_roadmaps import build_roadmap
from odin_backend.core.operational_planning.sustainability_engine import assess
from odin_backend.core.operator_relationship.adaptive_assistance import suggest_assistance
from odin_backend.core.operator_relationship.collaboration_style import adapt_style
from odin_backend.core.streaming.serializers import resolve_channels_for_trace


@pytest.fixture
def settings(tmp_path):
    db = tmp_path / "ops.db"
    return Settings(
        database_url=f"sqlite+aiosqlite:///{db.resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        runtime_enable_background_loops=False,
        operational_planning_enabled=True,
        operator_relationship_enabled=True,
        distributed_optimization_enabled=True,
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
async def test_project_operations(app):
    r = await app.operational_planning.project(goal="scale", horizon_weeks=4)
    assert r["accepted"] is True


@pytest.mark.asyncio
async def test_project_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        operational_planning_enabled=False,
        runtime_enable_background_loops=False,
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    r = await odin.operational_planning.project(goal="x")
    assert r["accepted"] is False
    await odin.shutdown()


@pytest.mark.asyncio
async def test_operator_interaction(app):
    e = await app.operator_relationship.record_interaction(kind="approve", detail="mission")
    assert e["kind"] == "approve"


@pytest.mark.asyncio
async def test_operator_snapshot(app):
    await app.operator_relationship.record_interaction(kind="view", detail="runtime")
    snap = await app.operator_relationship.snapshot()
    assert snap["recent_interactions"] >= 1


@pytest.mark.asyncio
async def test_distributed_optimize(app):
    await app.federation_runtime.connect_node(name="opt-peer", mode="trusted_cluster")
    r = await app.distributed_optimization.optimize()
    assert r["accepted"] is True


@pytest.mark.asyncio
async def test_distributed_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        distributed_optimization_enabled=False,
        runtime_enable_background_loops=False,
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    r = await odin.distributed_optimization.optimize()
    assert r["accepted"] is False
    await odin.shutdown()


def test_build_roadmap():
    r = build_roadmap(goal="g", milestones=5)
    assert len(r) == 5


def test_sustainability():
    s = assess(load=0.2, budget_remaining=1000)
    assert s["sustainable"] is True


def test_adapt_style():
    assert adapt_style(3) == "hands_on"
    assert adapt_style(50) == "autonomous_supervised"


def test_assistance_not_manipulative():
    a = suggest_assistance(style="balanced", context="test")
    assert a["manipulative"] is False


def test_topology_optimizer():
    t = optimize_topology(edge_count=3, node_count=4)
    assert "density" in t


def test_workload_balance():
    b = balance({"a": 10, "b": 20})
    assert b["balanced"] is True


def test_workload_channel():
    ev = TraceEvent(kind=TraceEventKind.WORKLOAD_REBALANCED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "optimization:runtime" in resolve_channels_for_trace(ev)


def test_operator_pattern_channel():
    ev = TraceEvent(kind=TraceEventKind.OPERATOR_PATTERN_LEARNED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "continuity:runtime" in resolve_channels_for_trace(ev)


@pytest.mark.parametrize("goal", ["scale", "optimize", "maintain", "recover", "plan"])
@pytest.mark.asyncio
async def test_goals(app, goal):
    r = await app.operational_planning.project(goal=goal)
    assert r["accepted"] is True


@pytest.mark.parametrize("weeks", [1, 2, 4, 8, 12])
@pytest.mark.asyncio
async def test_horizons(app, weeks):
    r = await app.operational_planning.project(goal="h", horizon_weeks=weeks)
    assert len(r["roadmap"]) == min(weeks, 10)


@pytest.mark.parametrize("kind", ["approve", "reject", "view", "spawn", "configure"])
@pytest.mark.asyncio
async def test_interactions(app, kind):
    e = await app.operator_relationship.record_interaction(kind=kind, detail="test")
    assert e["kind"] == kind


@pytest.mark.parametrize("i", range(25))
@pytest.mark.asyncio
async def test_many_interactions(app, i):
    await app.operator_relationship.record_interaction(kind=f"k_{i}", detail=f"d_{i}")
    snap = await app.operator_relationship.snapshot()
    assert snap["recent_interactions"] >= 1


@pytest.mark.parametrize("i", range(20))
@pytest.mark.asyncio
async def test_optimize_iterations(app, i):
    await app.federation_runtime.connect_node(name=f"node_{i}", mode="trusted_cluster")
    r = await app.distributed_optimization.optimize()
    assert r["accepted"] is True
