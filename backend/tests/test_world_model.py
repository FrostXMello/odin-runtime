"""World model and reasoning tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.reasoning.causal_inference import infer_causal
from odin_backend.core.reasoning.hypothesis_engine import HypothesisEngine
from odin_backend.core.reasoning.world_reasoner import WorldReasoner
from odin_backend.core.knowledge.world_model import WorldModel
from odin_backend.core.knowledge.belief_state import BeliefState
from odin_backend.core.knowledge.temporal_knowledge import TemporalKnowledge
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.streaming.serializers import resolve_channels_for_trace


@pytest.fixture
def settings(tmp_path):
    db = tmp_path / "world.db"
    return Settings(
        database_url=f"sqlite+aiosqlite:///{db.resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        runtime_enable_background_loops=False,
        knowledge_fabric_enabled=True,
        research_fabric_enabled=True,
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


def test_world_model_apply():
    wm = WorldModel()
    wm.apply_fact(entity="odin", fact="runtime active", confidence=0.7)
    snap = wm.snapshot()
    assert snap["entity_count"] == 1


def test_belief_revision():
    b = BeliefState()
    e1 = b.update("gpu", fact="prices high", confidence=0.6, source="web")
    e2 = b.update("gpu", fact="prices high", confidence=0.8, source="verified")
    assert e2["confidence"] == 0.8
    assert e1["previous_confidence"] is None or e2["previous_confidence"] == 0.6


def test_temporal_history():
    t = TemporalKnowledge()
    t.record(entity="ai", fact="models evolve", confidence=0.5)
    t.record(entity="ai", fact="models improve", confidence=0.7)
    assert len(t.history("ai")) == 2


def test_causal_inference():
    facts = [{"entity": "system", "fact": "load increase because traffic spike"}]
    links = infer_causal(facts)
    assert len(links) >= 1


def test_hypothesis_engine():
    h = HypothesisEngine()
    entry = h.add(topic="gpu", hypothesis="prices will rise", confidence=0.6)
    assert entry["topic"] == "gpu"
    assert len(h.list_all()) == 1


@pytest.mark.asyncio
async def test_world_reasoner_analyze(app):
    await app.knowledge_runtime.ingest_fact(entity="odin", fact="orchestration improves throughput", confidence=0.65)
    analysis = await app.reasoning_world.analyze(entity="odin")
    assert analysis["fact_count"] >= 1


@pytest.mark.asyncio
async def test_hypothesis_from_swarm(app):
    app.reasoning_world.record_hypothesis(topic="test", hypothesis="h1", confidence=0.5)
    snap = app.reasoning_world.snapshot()
    assert len(snap["hypotheses"]) >= 1


@pytest.mark.parametrize("i", range(15))
@pytest.mark.asyncio
async def test_world_model_growth(app, i):
    await app.knowledge_runtime.ingest_fact(entity=f"domain_{i % 5}", fact=f"observation {i}", confidence=0.5)
    wm = app.knowledge_runtime.snapshot()["world_model"]
    assert wm["entity_count"] >= 1


@pytest.mark.parametrize("fact", ["load causes latency", "traffic leads to saturation", "cache because faster"])
def test_causal_variants(fact):
    links = infer_causal([{"entity": "sys", "fact": fact}])
    assert isinstance(links, list)


def test_stream_world_model_channel():
    ev = TraceEvent(kind=TraceEventKind.WORLD_MODEL_UPDATED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "worldmodel:runtime" in resolve_channels_for_trace(ev)


def test_stream_hypothesis_channel():
    ev = TraceEvent(kind=TraceEventKind.HYPOTHESIS_GENERATED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "worldmodel:runtime" in resolve_channels_for_trace(ev)


@pytest.mark.parametrize("confidence", [0.1, 0.5, 0.9])
@pytest.mark.asyncio
async def test_belief_confidence_levels(app, confidence):
    await app.knowledge_runtime.ingest_fact(entity="metric", fact=f"level {confidence}", confidence=confidence)
    beliefs = app.knowledge_runtime.snapshot()["beliefs"]
    assert any(b.get("confidence") == confidence for b in beliefs)
