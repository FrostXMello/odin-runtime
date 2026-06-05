"""Knowledge fabric tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.knowledge.confidence_decay import decay_confidence, is_stale
from odin_backend.core.knowledge.contradiction_engine import detect_contradictions
from odin_backend.core.knowledge.knowledge_graph import KnowledgeGraph
from odin_backend.core.knowledge.knowledge_nodes import KnowledgeNode
from odin_backend.core.knowledge.research_governance import ResearchGovernance
from odin_backend.core.knowledge.semantic_entities import extract_entities
from odin_backend.core.knowledge.source_attribution import attribute_source
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.streaming.serializers import resolve_channels_for_trace
from datetime import datetime, timezone, timedelta


@pytest.fixture
def settings(tmp_path):
    db = tmp_path / "knowledge.db"
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


@pytest.mark.asyncio
async def test_app_has_knowledge_services(app):
    assert hasattr(app, "knowledge_runtime")
    assert hasattr(app, "research_fabric")
    assert hasattr(app, "web_access")
    assert hasattr(app, "research_agents")
    assert hasattr(app, "reasoning_world")
    assert hasattr(app, "research_governance")


@pytest.mark.parametrize(
    "text,expected_min",
    [
        ("Odin Runtime orchestrates Missions", 1),
        ("", 0),
        ("simple words only here", 1),
    ],
)
def test_extract_entities(text, expected_min):
    assert len(extract_entities(text)) >= expected_min


@pytest.mark.parametrize(
    "confidence,age,expected_max",
    [
        (0.8, 0, 0.81),
        (0.8, 30, 0.41),
        (0.2, 90, 0.1),
    ],
)
def test_decay_confidence(confidence, age, expected_max):
    assert decay_confidence(confidence=confidence, age_days=age) <= expected_max


def test_is_stale():
    old = datetime.now(timezone.utc) - timedelta(days=100)
    assert is_stale(updated_at=old) is True
    recent = datetime.now(timezone.utc) - timedelta(days=1)
    assert is_stale(updated_at=recent) is False


def test_contradiction_detection():
    items = [
        {"entity": "gpu", "fact": "prices increase", "confidence": 0.6},
        {"entity": "gpu", "fact": "prices decrease", "confidence": 0.5},
    ]
    assert len(detect_contradictions(items)) >= 1


def test_knowledge_graph_neighbors():
    g = KnowledgeGraph()
    g.link(source="odin", target="runtime", relation="part_of")
    assert "runtime" in g.neighbors("odin")


@pytest.mark.asyncio
async def test_ingest_fact_persists(app):
    node = await app.knowledge_runtime.ingest_fact(entity="odin", fact="local-first runtime", confidence=0.7)
    assert node["entity"] == "odin"
    listed = await app.knowledge_runtime.list_knowledge(entity="odin")
    assert any(n["fact"] == "local-first runtime" for n in listed)


@pytest.mark.asyncio
async def test_ingest_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        runtime_enable_background_loops=False,
        knowledge_fabric_enabled=False,
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    result = await odin.knowledge_runtime.ingest_fact(entity="x", fact="y")
    assert result["accepted"] is False
    await odin.shutdown()


@pytest.mark.asyncio
async def test_contradictions_endpoint_data(app):
    await app.knowledge_runtime.ingest_fact(entity="market", fact="demand increase", confidence=0.6)
    await app.knowledge_runtime.ingest_fact(entity="market", fact="demand decrease", confidence=0.5)
    found = await app.knowledge_runtime.contradictions()
    assert isinstance(found, list)


@pytest.mark.asyncio
async def test_belief_state_updated(app):
    await app.knowledge_runtime.ingest_fact(entity="belief", fact="test belief", confidence=0.55)
    beliefs = app.knowledge_runtime.snapshot()["beliefs"]
    assert len(beliefs) >= 1


@pytest.mark.asyncio
async def test_world_model_snapshot(app):
    await app.knowledge_runtime.ingest_fact(entity="world", fact="state updated", confidence=0.6)
    wm = app.knowledge_runtime.snapshot()["world_model"]
    assert wm["entity_count"] >= 1


def test_source_attribution():
    src = attribute_source(url="https://example.com", title="Example", trust=0.7)
    assert src["trust_score"] == 0.7
    assert "id" in src


@pytest.mark.asyncio
async def test_research_governance_blocks_harmful(app):
    assert app.research_governance.allow_research("malware exploit kit") is False


@pytest.mark.parametrize("kind", ["knowledge_created", "belief_updated", "world_model_updated"])
def test_stream_channels_knowledge(kind):
    ev = TraceEvent(kind=TraceEventKind(kind), trace_id="t", span_id="s", causal_chain_id="c")
    ch = resolve_channels_for_trace(ev)
    assert "knowledge:runtime" in ch or "beliefs:runtime" in ch or "worldmodel:runtime" in ch


@pytest.mark.parametrize("i", range(10))
@pytest.mark.asyncio
async def test_bulk_ingest(app, i):
    entity = f"entity_{i}"
    await app.knowledge_runtime.ingest_fact(entity=entity, fact=f"fact number {i}", confidence=0.5 + i * 0.01)
    nodes = await app.knowledge_runtime.list_knowledge(entity=entity)
    assert any(n["entity"] == entity for n in nodes)


def test_knowledge_node_model():
    n = KnowledgeNode(entity="test", fact="fact")
    assert n.confidence == 0.5
