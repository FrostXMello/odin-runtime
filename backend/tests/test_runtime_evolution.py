"""Runtime evolution tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.runtime_evolution.adaptive_throttling import throttle_factor
from odin_backend.core.runtime_evolution.policy_optimizer import optimize_policy
from odin_backend.core.runtime_evolution.reasoning_efficiency import efficiency
from odin_backend.core.runtime_evolution.routing_optimizer import optimize_routing
from odin_backend.core.streaming.serializers import resolve_channels_for_trace


@pytest.fixture
def settings(tmp_path):
    db = tmp_path / "evo.db"
    return Settings(
        database_url=f"sqlite+aiosqlite:///{db.resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        runtime_enable_background_loops=False,
        runtime_evolution_enabled=True,
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
async def test_optimize(app):
    r = await app.evolution_runtime.optimize()
    assert r["accepted"] is True


@pytest.mark.asyncio
async def test_optimize_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        runtime_evolution_enabled=False,
        runtime_enable_background_loops=False,
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    r = await odin.evolution_runtime.optimize()
    assert r["accepted"] is False
    await odin.shutdown()


@pytest.mark.asyncio
async def test_snapshot(app):
    await app.evolution_runtime.optimize()
    snap = app.evolution_runtime.snapshot()
    assert snap["cycles"] >= 1


@pytest.mark.asyncio
async def test_mission_economy(app):
    e = app.evolution_runtime.mission_economy("m-1")
    assert e["mission_id"] == "m-1"


def test_policy_optimizer_bounded():
    r = optimize_policy({"a": 0.5}, success_rate=0.9)
    assert r["delta_bounded"] is True
    assert all(0.1 <= v <= 1.0 for v in r["weights"].values())


def test_routing_optimizer():
    r = optimize_routing(latency_ms=100, success=0.8)
    assert r["optimized"] is True


def test_throttle():
    assert throttle_factor(load=1.0) == 0.5


def test_efficiency():
    e = efficiency(tokens=500, success=True, latency_ms=100)
    assert e["efficiency_score"] > 0


def test_evolution_channel():
    ev = TraceEvent(kind=TraceEventKind.EVOLUTION_CYCLE_COMPLETED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "evolution:runtime" in resolve_channels_for_trace(ev)


@pytest.mark.parametrize("i", range(30))
@pytest.mark.asyncio
async def test_optimize_cycles(app, i):
    r = await app.evolution_runtime.optimize()
    assert r["accepted"] is True


@pytest.mark.parametrize("rate", [0.3, 0.5, 0.7, 0.9])
def test_policy_rates(rate):
    r = optimize_policy({"x": 0.5, "y": 0.5}, success_rate=rate)
    assert "weights" in r


@pytest.mark.parametrize("cost", [0.1, 1.0, 5.0, 10.0])
@pytest.mark.asyncio
async def test_record_costs(app, cost):
    app.evolution_runtime.record_execution_cost(cost)
    assert app.evolution_runtime.snapshot()["economy"]["samples"] >= 1
