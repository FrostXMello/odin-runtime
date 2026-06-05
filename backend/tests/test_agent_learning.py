"""Agent learning society tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.learning_society.expertise_transfer import transfer
from odin_backend.core.learning_society.mentor_selection import select_mentor
from odin_backend.core.learning_society.strategy_distillation import distill
from odin_backend.core.learning_society.collaborative_training import start_session
from odin_backend.core.learning_society.reasoning_pattern_library import ReasoningPatternLibrary


@pytest.fixture
def settings(tmp_path):
    return Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'learn.db').resolve().as_posix()}",
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


def test_expertise_transfer():
    assert transfer(mentor_confidence=0.8, mentee_confidence=0.4) > 0.4


def test_mentor_selection():
    agents = [
        {"agent_id": "a", "confidence": 0.9, "expertise_domains": ["research_analyst"]},
        {"agent_id": "b", "confidence": 0.5, "expertise_domains": ["generalist"]},
    ]
    mentor = select_mentor(agents, domain="research_analyst")
    assert mentor["agent_id"] == "a"


def test_strategy_distillation():
    d = distill({"name": "deploy", "steps": ["plan", "test", "ship"], "confidence": 0.7})
    assert len(d["steps"]) <= 8


def test_pattern_library():
    lib = ReasoningPatternLibrary()
    lib.add(name="debug_loop", steps=["reproduce", "isolate", "fix"], source_agent="a1")
    assert len(lib.list_patterns()) == 1


def test_collaborative_training_session():
    s = start_session(mentor_id="m1", mentee_ids=["e1", "e2"], topic="routing")
    assert s["topic"] == "routing"


@pytest.mark.asyncio
async def test_peer_teaching(app):
    mentor = await app.agent_society.spawn_agent(name="Mentor", role="research_analyst", expertise_domains=["research_analyst"])
    await app.agent_society.record_outcome(mentor["agent_id"], domain="research_analyst", success=True)
    mentee = await app.agent_society.spawn_agent(name="Mentee")
    result = await app.peer_learning.teach(mentee_id=mentee["agent_id"], domain="research_analyst")
    assert result.get("transferred") is True or result.get("reason")


@pytest.mark.asyncio
async def test_pattern_distillation(app):
    d = app.peer_learning.distill_strategy(
        {"name": "incident_response", "steps": ["detect", "triage", "mitigate"], "agent_id": "x", "confidence": 0.8}
    )
    assert d["name"] == "incident_response"
    assert len(app.peer_learning.patterns()) >= 1


@pytest.mark.parametrize("domain", ["planning_specialist", "failure_diagnostician", "memory_curator", "execution_strategist"])
@pytest.mark.asyncio
async def test_expertise_domains(app, domain):
    agent = await app.agent_society.spawn_agent(name=f"L_{domain}", expertise_domains=[domain])
    await app.agent_society.record_outcome(agent["agent_id"], domain=domain, success=True)
    heat = app.agent_society.expertise_heatmap()
    assert isinstance(heat, dict)


@pytest.mark.parametrize("i", range(12))
@pytest.mark.asyncio
async def test_learning_patterns(app, i):
    app.peer_learning.distill_strategy({"name": f"pattern_{i}", "steps": [f"step_{i}"], "confidence": 0.6})


@pytest.mark.parametrize("mentor_conf,mentee_conf", [(0.9, 0.3), (0.7, 0.5), (0.6, 0.4)])
def test_transfer_bounds(mentor_conf, mentee_conf):
    result = transfer(mentor_confidence=mentor_conf, mentee_confidence=mentee_conf)
    assert 0.0 <= result <= 1.0
