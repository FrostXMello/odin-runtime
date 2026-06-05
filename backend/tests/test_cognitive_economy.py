"""Cognitive economy tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.cognitive_economy.cognition_budgeting import CognitionBudgeting
from odin_backend.core.cognitive_economy.compute_allocator import allocate
from odin_backend.core.cognitive_economy.model_cost_balancer import select_model
from odin_backend.core.cognitive_economy.mission_valuation import value_mission
from odin_backend.core.cognitive_economy.reasoning_priority import priority_score
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.streaming.serializers import resolve_channels_for_trace


@pytest.fixture
def settings(tmp_path):
    db = tmp_path / "econ.db"
    return Settings(
        database_url=f"sqlite+aiosqlite:///{db.resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        runtime_enable_background_loops=False,
        cognitive_economy_enabled=True,
        cognitive_economy_mode="balanced",
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
async def test_charge(app):
    r = app.cognitive_economy.charge(mission_id="m-1", tokens=100)
    assert r["accepted"] is True


@pytest.mark.asyncio
async def test_budget_exceeded(app):
    for _ in range(200):
        app.cognitive_economy.charge(mission_id=None, tokens=100)
    r = app.cognitive_economy.charge(mission_id=None, tokens=50000)
    assert r["accepted"] is False


@pytest.mark.asyncio
async def test_mission_economy(app):
    app.cognitive_economy.charge(mission_id="m-e", tokens=500)
    e = app.cognitive_economy.mission_economy("m-e")
    assert e["tokens"] == 500


@pytest.mark.asyncio
async def test_set_mode(app):
    snap = app.cognitive_economy.set_mode("low_resource")
    assert snap["mode"] == "low_resource"


def test_budget_modes():
    b = CognitionBudgeting(mode="high_performance")
    assert b.snapshot()["tokens"] == 20000


def test_allocate():
    a = allocate(available=100, demands=[10, 20, 30])
    assert abs(sum(a) - 100) < 0.1


def test_select_model():
    assert select_model(mode="low_resource", task_complexity=0.9) == "mock"


def test_priority_score():
    assert priority_score(urgency=0.8, value=0.7, cost=0.2) > 0


def test_value_mission():
    v = value_mission(priority="high", complexity=0.5)
    assert v["value_score"] > 0.5


def test_economy_channel():
    ev = TraceEvent(kind=TraceEventKind.COGNITION_BUDGET_UPDATED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "economy:runtime" in resolve_channels_for_trace(ev)


@pytest.mark.parametrize("mode", ["low_resource", "balanced", "high_performance"])
@pytest.mark.asyncio
async def test_modes(app, mode):
    snap = app.cognitive_economy.set_mode(mode)
    assert snap["mode"] == mode


@pytest.mark.parametrize("tokens", [10, 50, 100, 500, 1000])
@pytest.mark.asyncio
async def test_charges(app, tokens):
    r = app.cognitive_economy.charge(mission_id="t", tokens=tokens)
    assert r["accepted"] is True


@pytest.mark.parametrize("i", range(25))
@pytest.mark.asyncio
async def test_mission_charges(app, i):
    app.cognitive_economy.charge(mission_id=f"m-{i}", tokens=50)
    assert app.cognitive_economy.mission_economy(f"m-{i}")["tokens"] == 50
