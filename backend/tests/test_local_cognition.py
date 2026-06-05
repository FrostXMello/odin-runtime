"""Local model cognitive layer tests."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.cognition.reasoning.relevance_scoring import rank_items, score_relevance
from odin_backend.core.cognition.reflection.contradiction_detection import detect_contradictions
from odin_backend.core.cognition.reflection.reasoning_validation import (
    hallucination_risk_score,
    validate_strategy,
)
from odin_backend.core.embeddings.chunking import chunk_text
from odin_backend.core.models.context_windowing import fit_messages, truncate_text
from odin_backend.core.models.model_profiles import ModelCapabilityTag
from odin_backend.core.models.providers.mock import MockProvider
from odin_backend.core.models.registry import LocalModelRegistry
from odin_backend.core.models.tokenizer import estimate_tokens
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.resources.ram_monitor import memory_pressure, ram_status


@pytest.fixture
def settings(tmp_path):
    db = tmp_path / "local_cog.db"
    return Settings(
        database_url=f"sqlite+aiosqlite:///{db.resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        runtime_enable_background_loops=False,
        conscious_loop_enabled=False,
        cognitive_learning_enabled=False,
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


# --- Model runtime ---


def test_model_registry_defaults(settings):
    reg = LocalModelRegistry(settings)
    assert reg.list_profiles()
    assert reg.provider.name == "mock"


@pytest.mark.asyncio
async def test_mock_provider_complete():
    p = MockProvider()
    await p.load_model("mock-reasoning")
    out = await p.complete(model="mock-reasoning", messages=[{"role": "user", "content": "plan deploy"}])
    assert "mock" in out


@pytest.mark.asyncio
async def test_mock_provider_embed():
    p = MockProvider()
    vecs = await p.embed(model="mock-embed", texts=["hello", "world"])
    assert len(vecs) == 2


@pytest.mark.asyncio
async def test_model_manager_load(app):
    prof = await app.model_manager.load("mock-reasoning")
    assert prof.loaded


def test_estimate_tokens():
    assert estimate_tokens("one two three four") >= 4


def test_truncate_text():
    long = "word " * 500
    out, truncated = truncate_text(long, max_tokens=50)
    assert truncated


def test_fit_messages():
    msgs = [{"role": "user", "content": "x" * 2000} for _ in range(10)]
    fitted, truncated = fit_messages(msgs, max_tokens=200)
    assert len(fitted) < len(msgs) or truncated


# --- Routing ---


@pytest.mark.asyncio
async def test_inference_router(app):
    route = app.model_manager.runtime.router.route_payload(task_kind="planning", payload={})
    assert route["model"]


@pytest.mark.asyncio
async def test_model_selector(app):
    from odin_backend.core.models.routing.model_selector import ModelSelector

    sel = ModelSelector(app.model_registry, app=app)
    model = sel.select(task="plan", reasoning_depth="deep")
    assert model


# --- Memory grounding ---


@pytest.mark.asyncio
async def test_reasoning_context_build(app):
    ctx = await app.reasoning_pipeline.build(objective="deploy api service", mission_id="m1")
    assert "prompt_block" in ctx


def test_relevance_scoring():
    assert score_relevance("deploy api", {"label": "deploy pipeline", "confidence": 0.8, "score": 0.7}) > 0.3


def test_rank_items():
    items = rank_items("python", [{"label": "python run", "score": 0.9}, {"label": "cooking", "score": 0.1}])
    assert items[0]["label"].startswith("python")


# --- Embeddings ---


def test_chunk_text():
    chunks = chunk_text("a" * 1000, max_chars=300)
    assert len(chunks) >= 2


@pytest.mark.asyncio
async def test_embedding_index(app):
    ids = await app.embedding_runtime.embed_and_index("semantic memory chunk for testing")
    assert ids
    hits = await app.embedding_runtime.hybrid_search("semantic memory", limit=3)
    assert isinstance(hits, list)


# --- Reflection ---


def test_contradiction_detection():
    issues = detect_contradictions("Run parallel steps then execute sequential workflow")
    assert issues


def test_hallucination_risk():
    risk = hallucination_risk_score("probably might assume unknown api", grounding_size=10)
    assert risk > 0.4


def test_validate_strategy():
    v = validate_strategy("use shell.safe", {"shell.safe": {"failure_rate": 0.7}})
    assert not v["valid"]


@pytest.mark.asyncio
async def test_reflection_engine(app):
    result = await app.cognitive_reflection.reflect(
        plan="parallel deploy then sequential rollback",
        objective="deploy service",
        mission_id="m-ref",
    )
    assert "critique" in result


@pytest.mark.asyncio
async def test_reflection_recursion_guard(app):
    app.settings.reflection_max_depth = 1
    r = await app.cognitive_reflection.reflect(
        plan="plan",
        objective="obj",
        mission_id="m-depth",
        depth=1,
    )
    assert r.get("skipped") is True


# --- Agents ---


@pytest.mark.asyncio
async def test_cognitive_agent_pipeline(app):
    result = await app.cognitive_agents.run_pipeline(objective="analyze logs", mission_id="m-agents")
    assert len(result["steps"]) >= 4


# --- Resources ---


def test_ram_status():
    st = ram_status()
    assert "available_mb" in st


def test_memory_pressure():
    assert 0 <= memory_pressure() <= 1.0


@pytest.mark.asyncio
async def test_resource_scheduler(app):
    st = app.model_resource_scheduler.status()
    assert "ram" in st


# --- Inference ---


@pytest.mark.asyncio
async def test_runtime_infer(app):
    out = await app.model_manager.runtime.infer(
        messages=[{"role": "user", "content": "Summarize mission"}],
        task_kind="planning",
    )
    assert isinstance(out, str)


@pytest.mark.asyncio
async def test_inference_cancellation(app):
    ok = app.model_manager.runtime.cancel("nonexistent-id")
    assert ok in (True, False)


# --- APIs ---


@pytest.mark.asyncio
async def test_models_api(app):
    from odin_backend.api.routes import models_runtime

    api = FastAPI()
    api.state.odin = app
    api.include_router(models_runtime.router, prefix="/api/v1")
    transport = ASGITransport(app=api)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/api/v1/runtime/models")
        assert r.status_code == 200
        r2 = await client.post("/api/v1/runtime/reasoning/run", json={"objective": "test objective"})
        assert r2.status_code == 200


@pytest.mark.asyncio
async def test_stream_channels_local_cognition():
    from odin_backend.core.streaming.serializers import resolve_channels_for_trace

    ev = TraceEvent(
        kind=TraceEventKind.INFERENCE_STARTED,
        trace_id="t",
        span_id="s",
        causal_chain_id="c",
    )
    ch = resolve_channels_for_trace(ev)
    assert "models:runtime" in ch


@pytest.mark.asyncio
async def test_app_has_local_cognition(app):
    assert hasattr(app, "model_manager")
    assert hasattr(app, "reasoning_pipeline")
    assert hasattr(app, "cognitive_reflection")
    assert hasattr(app, "cognitive_agents")
