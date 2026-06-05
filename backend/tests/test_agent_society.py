"""Agent society tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.agent_society.personality_bounds import bounded_update
from odin_backend.core.agent_society.specialization import evolve_expertise, rebalance
from odin_backend.core.agent_society.consensus_engine import reach_consensus
from odin_backend.core.app import OdinApplication
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.streaming.serializers import resolve_channels_for_trace


@pytest.fixture
def settings(tmp_path):
    db = tmp_path / "society.db"
    return Settings(
        database_url=f"sqlite+aiosqlite:///{db.resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        runtime_enable_background_loops=False,
        conscious_loop_enabled=False,
        cognitive_learning_enabled=False,
        local_cognition_enabled=True,
        model_provider="mock",
        agent_society_enabled=True,
        knowledge_fabric_enabled=True,
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


@pytest.mark.asyncio
async def test_app_has_society_services(app):
    assert hasattr(app, "agent_society")
    assert hasattr(app, "agent_messages")
    assert hasattr(app, "peer_learning")


@pytest.mark.asyncio
async def test_spawn_agent(app):
    agent = await app.agent_society.spawn_agent(name="Mimir", role="memory_curator")
    assert agent["name"] == "Mimir"
    assert agent["role"] == "memory_curator"


@pytest.mark.asyncio
async def test_spawn_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        runtime_enable_background_loops=False,
        agent_society_enabled=False,
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    result = await odin.agent_society.spawn_agent(name="X")
    assert result["accepted"] is False
    await odin.shutdown()


@pytest.mark.asyncio
async def test_continuity_restore_on_startup(app):
    agent = await app.agent_society.spawn_agent(name="ContinuityTest")
    await app.agent_society._continuity.checkpoint(
        agent["agent_id"], thought={"topic": "research"}, memory={"step": 2}, objectives=["finish"]
    )
    restored = await app.agent_society._continuity.restore(agent["agent_id"])
    assert restored["thought_context"]["topic"] == "research"


@pytest.mark.parametrize("success", [True, False])
@pytest.mark.asyncio
async def test_expertise_evolution(app, success):
    agent = await app.agent_society.spawn_agent(name=f"Agent_{success}", role="planner")
    result = await app.agent_society.record_outcome(agent["agent_id"], domain="planning_specialist", success=success)
    assert "confidence" in result


@pytest.mark.asyncio
async def test_delegation(app):
    a1 = await app.agent_society.spawn_agent(name="Delegator")
    a2 = await app.agent_society.spawn_agent(name="Delegatee")
    d = await app.agent_society.create_delegation(
        from_agent=a1["agent_id"], to_agent=a2["agent_id"], task="Analyze logs"
    )
    assert d["status"] == "pending"


@pytest.mark.asyncio
async def test_dialogue(app):
    agents = []
    for name in ("A", "B", "C"):
        agents.append((await app.agent_society.spawn_agent(name=name))["agent_id"])
    session = await app.agent_society.start_dialogue(topic="Infrastructure review", participant_ids=agents)
    assert session["topic"] == "Infrastructure review"


@pytest.mark.asyncio
async def test_consensus():
    result = reach_consensus([{"approve": True, "weight": 1.0}, {"approve": True, "weight": 0.8}])
    assert result["consensus"] is True


@pytest.mark.parametrize("delta", [-0.2, -0.1, 0.0, 0.1, 0.2])
def test_bounded_traits(delta):
    assert 0.0 <= bounded_update(0.5, delta) <= 1.0


@pytest.mark.parametrize("conf", [0.3, 0.5, 0.7, 0.9])
def test_specialization_evolve(conf):
    updated, _ = evolve_expertise(conf, success=True, domain="research_analyst")
    assert updated >= conf - 0.15


def test_rebalance():
    assert rebalance(0.8) <= 0.8


@pytest.mark.parametrize("kind", ["agent_spawned", "expertise_updated", "delegation_created"])
def test_stream_channels_society(kind):
    ev = TraceEvent(kind=TraceEventKind(kind), trace_id="t", span_id="s", causal_chain_id="c")
    ch = resolve_channels_for_trace(ev)
    assert "society:runtime" in ch or "agents:runtime" in ch


@pytest.mark.parametrize("i", range(10))
@pytest.mark.asyncio
async def test_population_limit(app, i, settings):
    settings.agent_society_max_agents = 3
    app.agent_society._governance._app.settings = settings
    for _ in range(3):
        await app.agent_society.spawn_agent(name=f"Fill_{_}")
    blocked = await app.agent_society.spawn_agent(name="Overflow")
    if i == 0:
        assert blocked.get("accepted") is False or blocked.get("name") != "Overflow"
