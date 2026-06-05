"""Prompt 34 production runtime — agent execution tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.agent_execution.recursive_subtasks import decompose
from odin_backend.core.agent_execution.task_negotiation import negotiate
from odin_backend.core.app import OdinApplication
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.streaming.serializers import resolve_channels_for_trace


@pytest.fixture
def settings(tmp_path):
    db = tmp_path / "prod.db"
    return Settings(
        database_url=f"sqlite+aiosqlite:///{db.resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        runtime_enable_background_loops=False,
        conscious_loop_enabled=False,
        model_provider="mock",
        local_cognition_enabled=True,
        local_ai_enabled=True,
        vector_memory_enabled=True,
        agent_execution_enabled=True,
        agent_society_enabled=True,
        copilot_production_enabled=True,
        realtime_voice_enabled=True,
        evaluation_enabled=True,
        resource_optimization_enabled=True,
        daemon_mode_enabled=True,
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
async def test_app_has_agent_execution(app):
    assert hasattr(app, "agent_execution")


@pytest.mark.asyncio
async def test_spawn_task(app):
    r = await app.agent_execution.spawn_task(owner_agent_id="agent-1", title="deploy release")
    assert r["accepted"] is True
    assert r["task"]["task_id"]
    assert r["subtasks"]


@pytest.mark.asyncio
async def test_spawn_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        agent_execution_enabled=False,
        runtime_enable_background_loops=False,
        model_provider="mock",
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    r = await odin.agent_execution.spawn_task(owner_agent_id="a", title="t")
    assert r["accepted"] is False
    await odin.shutdown()


@pytest.mark.asyncio
async def test_negotiate_ownership(app):
    r = await app.agent_execution.negotiate_ownership(agent_ids=["a1", "a2", "a3"], task_title="review code")
    assert r["owner"] in ("a1", "a2", "a3")
    assert r["task"] == "review code"


@pytest.mark.asyncio
async def test_resume_pending(app):
    await app.agent_execution.spawn_task(owner_agent_id="agent-r", title="pending work")
    resumed = await app.agent_execution.resume_pending()
    assert isinstance(resumed, list)


@pytest.mark.asyncio
async def test_snapshot(app):
    await app.agent_execution.spawn_task(owner_agent_id="agent-s", title="snapshot task")
    snap = app.agent_execution.snapshot()
    assert "scheduler_queue" in snap
    assert snap["scheduler_queue"] >= 1


def test_task_delegated_channel():
    ev = TraceEvent(kind=TraceEventKind.TASK_DELEGATED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "agents:runtime" in resolve_channels_for_trace(ev)


def test_decompose_unit():
    subs = decompose("migrate database", depth=4)
    assert len(subs) == 4
    assert subs[0]["level"] == 0


def test_negotiate_unit():
    r = negotiate([{"agent_id": "x", "confidence": 0.9}, {"agent_id": "y", "confidence": 0.4}], "task")
    assert r["owner"] == "x"


@pytest.mark.parametrize("i", range(35))
@pytest.mark.asyncio
async def test_spawn_bulk(app, i):
    r = await app.agent_execution.spawn_task(
        owner_agent_id=f"agent-{i}",
        title=f"bulk task {i}",
        mission_id=f"mission-{i % 5}",
    )
    assert r["accepted"] is True


@pytest.mark.parametrize("agent_count", [2, 3, 4, 5])
@pytest.mark.asyncio
async def test_negotiate_agent_counts(app, agent_count):
    agents = [f"agent-{j}" for j in range(agent_count)]
    r = await app.agent_execution.negotiate_ownership(agent_ids=agents, task_title="shared objective")
    assert r["owner"] in agents


@pytest.mark.parametrize("i", range(15))
@pytest.mark.asyncio
async def test_resume_bulk(app, i):
    await app.agent_execution.spawn_task(owner_agent_id=f"resume-agent-{i}", title=f"resume task {i}")
    pending = await app.agent_execution.resume_pending()
    assert isinstance(pending, list)


@pytest.mark.parametrize("title", ["plan", "execute", "verify", "rollback", "monitor"])
@pytest.mark.asyncio
async def test_spawn_titles(app, title):
    r = await app.agent_execution.spawn_task(owner_agent_id="title-agent", title=title)
    assert r["accepted"] is True
    assert any(title in s["subtask"] for s in r["subtasks"])


@pytest.mark.parametrize("depth", [1, 2, 3, 4, 5])
def test_decompose_depths(depth):
    subs = decompose("objective", depth=depth)
    assert len(subs) == min(depth, 5)


@pytest.mark.parametrize("confidence", [0.2, 0.4, 0.6, 0.8])
def test_negotiate_confidence(confidence):
    agents = [{"agent_id": "low", "confidence": 0.1}, {"agent_id": "high", "confidence": confidence}]
    r = negotiate(agents, "pick owner")
    assert r["owner"] == "high" if confidence >= 0.1 else "low"
