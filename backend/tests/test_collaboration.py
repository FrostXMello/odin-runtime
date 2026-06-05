"""Society collaboration tests."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from odin_backend.api.routes import society_runtime
from odin_backend.config import Settings
from odin_backend.core.agent_messages.negotiation_protocol import negotiate_accept, negotiate_proposal
from odin_backend.core.agent_messages.structured_dialogue import build_message
from odin_backend.core.agent_society.collaboration_graph import CollaborationGraph
from odin_backend.core.app import OdinApplication


@pytest.fixture
def settings(tmp_path):
    return Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'collab.db').resolve().as_posix()}",
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


def test_collaboration_graph():
    g = CollaborationGraph()
    g.link("a", "b")
    g.link("b", "c")
    assert "b" in g.neighbors("a")


def test_negotiation_protocol():
    p = negotiate_proposal(proposer="a1", role="planner", task="deploy")
    accepted = negotiate_accept(p)
    assert accepted["status"] == "accepted"


def test_structured_message():
    m = build_message(sender="a", kind="request", content="help", recipients=["b"])
    assert m["sender"] == "a"


@pytest.mark.asyncio
async def test_message_bus(app):
    a = await app.agent_society.spawn_agent(name="Sender")
    b = await app.agent_society.spawn_agent(name="Receiver")
    msg = await app.agent_messages.broadcast(
        sender=a["agent_id"], kind="assist", content="Need review", recipients=[b["agent_id"]]
    )
    assert msg.get("id")
    inbox = app.agent_messages.inbox(b["agent_id"])
    assert len(inbox) >= 1


@pytest.mark.asyncio
async def test_form_team(app):
    ids = []
    for n in ("T1", "T2"):
        ids.append((await app.agent_society.spawn_agent(name=n))["agent_id"])
    team = await app.agent_society.form_team(template="research_squad", agent_ids=ids)
    assert team["template"] == "research_squad"


@pytest.mark.asyncio
async def test_negotiate_task(app):
    ids = [(await app.agent_society.spawn_agent(name=f"N{i}", role="planner"))["agent_id"] for i in range(2)]
    roles = await app.agent_society.negotiate_task(task="Plan migration", agent_ids=ids)
    assert len(roles) == 2


@pytest.mark.asyncio
async def test_consensus_reached(app):
    result = await app.agent_society.run_consensus(
        [{"approve": True, "weight": 1.0}, {"approve": True, "weight": 1.0}, {"approve": False, "weight": 0.5}]
    )
    assert "confidence" in result


@pytest.mark.parametrize("template", ["research_squad", "infrastructure_council", "planning_committee", "unknown"])
@pytest.mark.asyncio
async def test_team_templates(app, template):
    aid = (await app.agent_society.spawn_agent(name=f"Team_{template}"))["agent_id"]
    team = await app.agent_society.form_team(template=template, agent_ids=[aid])
    assert team["id"]


@pytest.mark.parametrize("i", range(15))
@pytest.mark.asyncio
async def test_collaboration_messages(app, i):
    a = (await app.agent_society.spawn_agent(name=f"S{i}"))["agent_id"]
    b = (await app.agent_society.spawn_agent(name=f"R{i}"))["agent_id"]
    await app.agent_messages.broadcast(sender=a, kind="ping", content=f"msg {i}", recipients=[b])


@pytest.mark.asyncio
async def test_society_api(app):
    api = FastAPI()
    api.state.odin = app
    api.include_router(society_runtime.router, prefix="/api/v1")
    transport = ASGITransport(app=api)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        assert (await client.get("/api/v1/runtime/society")).status_code == 200
        assert (await client.get("/api/v1/runtime/society/collaboration")).status_code == 200
        assert (await client.get("/api/v1/runtime/society/dialogues")).status_code == 200


@pytest.mark.parametrize("task", ["deploy", "research", "debug", "optimize"])
@pytest.mark.asyncio
async def test_delegation_tasks(app, task):
    a1 = (await app.agent_society.spawn_agent(name=f"D1_{task}"))["agent_id"]
    a2 = (await app.agent_society.spawn_agent(name=f"D2_{task}"))["agent_id"]
    d = await app.agent_society.create_delegation(from_agent=a1, to_agent=a2, task=task)
    assert d["task"] == task
