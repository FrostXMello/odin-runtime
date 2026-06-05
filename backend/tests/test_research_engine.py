"""Research fabric tests."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from odin_backend.api.routes import knowledge_runtime
from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.research_engine.citation_engine import build_citations
from odin_backend.core.research_engine.contradiction_resolver import resolve_from_evidence
from odin_backend.core.research_engine.research_planner import plan_research
from odin_backend.core.research_engine.source_ranking import rank_sources
from odin_backend.core.research_engine.trend_analysis import analyze_trends
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.streaming.serializers import resolve_channels_for_trace


@pytest.fixture
def settings(tmp_path):
    db = tmp_path / "research.db"
    return Settings(
        database_url=f"sqlite+aiosqlite:///{db.resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        runtime_enable_background_loops=False,
        conscious_loop_enabled=False,
        cognitive_learning_enabled=False,
        local_cognition_enabled=True,
        model_provider="mock",
        knowledge_fabric_enabled=True,
        research_fabric_enabled=True,
        web_access_enabled=False,
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


def test_plan_research():
    subs = plan_research("GPU pricing")
    assert len(subs) >= 3
    assert any("GPU" in s for s in subs)


def test_rank_sources():
    sources = [
        {"url": "https://a.com", "title": "GPU pricing", "trust_score": 0.4},
        {"url": "https://b.com", "title": "Other", "trust_score": 0.9},
    ]
    ranked = rank_sources(sources, topic="GPU")
    assert ranked[0]["trust_score"] >= 0.4


def test_citations():
    cites = build_citations([{"url": "https://x.com", "title": "X"}])
    assert cites[0]["ref"] == "[1]"


def test_trend_analysis():
    hist = [{"confidence": 0.4}, {"confidence": 0.6}]
    trends = analyze_trends(hist)
    assert trends[0]["direction"] == "rising"


def test_contradiction_resolver():
    evidence = [{"title": "a", "content": "prices increase", "trust_score": 0.5}, {"title": "a", "content": "prices decrease", "trust_score": 0.5}]
    assert len(resolve_from_evidence(evidence)) >= 1


@pytest.mark.asyncio
async def test_research_session(app):
    session = await app.research_fabric.start(topic="orchestration architectures")
    assert session.get("topic") == "orchestration architectures"
    assert "report" in session


@pytest.mark.asyncio
async def test_research_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        runtime_enable_background_loops=False,
        research_fabric_enabled=False,
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    result = await odin.research_fabric.start(topic="test")
    assert result["accepted"] is False
    await odin.shutdown()


@pytest.mark.asyncio
async def test_verify_source(app):
    result = await app.research_fabric.verify_source(url="https://example.com/docs")
    assert "verified" in result


@pytest.mark.asyncio
async def test_swarm_investigation(app):
    result = await app.research_agents.investigate(topic="AI", evidence=[{"url": "https://x.com", "status": "stub", "trust_score": 0.6}])
    assert len(result["agents"]) == 6


@pytest.mark.parametrize("topic", ["GPU trends", "local models", "execution pools", "orchestration"])
@pytest.mark.asyncio
async def test_research_topics(app, topic):
    session = await app.research_fabric.research_topic(topic=topic)
    assert session["topic"] == topic


@pytest.mark.parametrize("kind", ["research_started", "research_completed", "source_verified", "trend_detected"])
def test_stream_channels_research(kind):
    ev = TraceEvent(kind=TraceEventKind(kind), trace_id="t", span_id="s", causal_chain_id="c")
    ch = resolve_channels_for_trace(ev)
    assert "research:runtime" in ch or "trends:runtime" in ch


@pytest.mark.asyncio
async def test_knowledge_api(app):
    api = FastAPI()
    api.state.odin = app
    api.include_router(knowledge_runtime.router, prefix="/api/v1")
    transport = ASGITransport(app=api)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        assert (await client.get("/api/v1/runtime/knowledge")).status_code == 200
        r = await client.post("/api/v1/runtime/research/start", json={"topic": "test topic"})
        assert r.status_code == 200
        assert (await client.get("/api/v1/runtime/world-model")).status_code == 200
        assert (await client.get("/api/v1/runtime/beliefs")).status_code == 200
        assert (await client.get("/api/v1/runtime/contradictions")).status_code == 200
        assert (await client.get("/api/v1/runtime/sources")).status_code == 200


@pytest.mark.parametrize("i", range(8))
@pytest.mark.asyncio
async def test_repeated_research(app, i):
    topic = f"topic_{i}"
    session = await app.research_fabric.start(topic=topic)
    assert session.get("topic") == topic
    snap = app.research_fabric.snapshot()
    assert len(snap["sessions"]) >= 1
