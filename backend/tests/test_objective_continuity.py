"""Objective continuity tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.streaming.serializers import resolve_channels_for_trace


@pytest.fixture
def settings(tmp_path):
    return Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'obj.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        runtime_enable_background_loops=False,
        agent_society_enabled=True,
        knowledge_fabric_enabled=True,
        local_cognition_enabled=True,
        model_provider="mock",
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
async def test_create_objective(app):
    agent = await app.agent_society.spawn_agent(name="ObjectiveOwner")
    obj = await app.agent_society.create_objective(owner_agent_id=agent["agent_id"], title="Monitor GPU pricing")
    assert obj["title"] == "Monitor GPU pricing"


@pytest.mark.asyncio
async def test_objective_persistence(app):
    agent = await app.agent_society.spawn_agent(name="PersistOwner")
    await app.agent_society.create_objective(owner_agent_id=agent["agent_id"], title="Long horizon goal")
    objs = await app.agent_society._objectives.list_for_agent(agent["agent_id"])
    assert len(objs) >= 1


@pytest.mark.asyncio
async def test_continuity_checkpoint_objectives(app):
    agent = await app.agent_society.spawn_agent(name="CheckpointAgent")
    await app.agent_society._continuity.checkpoint(
        agent["agent_id"],
        thought={"focus": "investigation"},
        memory={"step": 5},
        objectives=["finish research", "write report"],
    )
    restored = await app.agent_society._continuity.restore(agent["agent_id"])
    assert len(restored["active_objectives"]) == 2


@pytest.mark.parametrize("title", [f"Objective {i}" for i in range(20)])
@pytest.mark.asyncio
async def test_many_objectives(app, title):
    agent = await app.agent_society.spawn_agent(name=f"Owner_{title[:8]}")
    await app.agent_society.create_objective(owner_agent_id=agent["agent_id"], title=title)


@pytest.mark.parametrize("i", range(10))
@pytest.mark.asyncio
async def test_objective_list_grows(app, i):
    agent = await app.agent_society.spawn_agent(name=f"List_{i}")
    await app.agent_society.create_objective(owner_agent_id=agent["agent_id"], title=f"Goal {i}")
    all_objs = await app.agent_society._objectives.list_all()
    assert len(all_objs) >= 1
    agent_objs = await app.agent_society._objectives.list_for_agent(agent["agent_id"])
    assert len(agent_objs) >= 1


def test_continuity_restored_channel():
    ev = TraceEvent(kind=TraceEventKind.CONTINUITY_RESTORED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "objectives:runtime" in resolve_channels_for_trace(ev)


def test_objective_assigned_channel():
    ev = TraceEvent(kind=TraceEventKind.OBJECTIVE_ASSIGNED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "objectives:runtime" in resolve_channels_for_trace(ev)


@pytest.mark.parametrize("domain", ["planning", "research", "execution", "memory"])
@pytest.mark.asyncio
async def test_outcome_updates_knowledge(app, domain):
    agent = await app.agent_society.spawn_agent(name=f"K_{domain}")
    await app.agent_society.record_outcome(agent["agent_id"], domain=domain, success=True)
    nodes = await app.knowledge_runtime.list_knowledge(entity=f"agent:{agent['agent_id']}")
    assert len(nodes) >= 1
