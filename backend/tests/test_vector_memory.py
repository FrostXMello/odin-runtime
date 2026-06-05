"""Prompt 34 production runtime — vector memory and local AI tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.streaming.serializers import resolve_channels_for_trace
from odin_backend.core.vector_memory.chunking import chunk_with_importance
from odin_backend.core.vector_memory.episodic_memory import EpisodicMemory
from odin_backend.core.vector_memory.semantic_cache import SemanticCache


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
async def test_app_has_vector_memory(app):
    assert hasattr(app, "vector_memory")
    assert hasattr(app, "local_ai")
    assert hasattr(app, "embedding_runtime")


@pytest.mark.asyncio
async def test_ingest_accepted(app):
    r = await app.vector_memory.ingest("deploy service to staging", metadata={"importance": 0.8})
    assert r["accepted"] is True
    assert "ids" in r


@pytest.mark.asyncio
async def test_ingest_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        vector_memory_enabled=False,
        runtime_enable_background_loops=False,
        model_provider="mock",
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    r = await odin.vector_memory.ingest("blocked")
    assert r["accepted"] is False
    await odin.shutdown()


@pytest.mark.asyncio
async def test_ingest_deduplicated(app):
    text = "unique memory payload for dedup"
    first = await app.vector_memory.ingest(text)
    second = await app.vector_memory.ingest(text)
    assert first["accepted"] is True
    assert second.get("deduplicated") is True


@pytest.mark.asyncio
async def test_search_returns_list(app):
    await app.vector_memory.ingest("searchable knowledge about kubernetes")
    results = await app.vector_memory.search("kubernetes", limit=3)
    assert isinstance(results, list)


@pytest.mark.asyncio
async def test_snapshot_fields(app):
    await app.vector_memory.ingest("snapshot probe text")
    snap = app.vector_memory.snapshot()
    assert "cache_size" in snap
    assert "episodes" in snap
    assert "long_term" in snap


def test_record_episode(app):
    ep = app.vector_memory.record_episode(event="ingest", context={"source": "test"})
    assert ep["event"] == "ingest"
    assert app.vector_memory.snapshot()["episodes"] >= 1


def test_memory_indexed_channel():
    ev = TraceEvent(kind=TraceEventKind.MEMORY_INDEXED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "memory:runtime" in resolve_channels_for_trace(ev)


def test_chunk_with_importance_unit():
    chunks = chunk_with_importance("word " * 200, chunk_size=256)
    assert chunks
    assert all("importance" in c for c in chunks)


def test_semantic_cache_unit():
    cache = SemanticCache()
    cache.put("hello", {"ids": ["a"]})
    assert cache.get("hello")["ids"] == ["a"]
    assert cache.size() == 1


def test_episodic_replay_unit():
    mem = EpisodicMemory()
    mem.record(event="e1", context={"k": 1})
    mem.record(event="e2", context={"k": 2})
    replay = mem.replay(limit=5)
    assert len(replay) == 2


@pytest.mark.asyncio
async def test_local_ai_generate(app):
    r = await app.local_ai.generate(prompt="summarize deployment status", template="summary")
    assert "text" in r
    assert r["model"]


@pytest.mark.asyncio
async def test_local_ai_route_model(app):
    r = await app.local_ai.route_model(complexity=0.8, token_budget=4096)
    assert r["role"] in ("reasoning", "code", "fast")


@pytest.mark.asyncio
async def test_local_ai_warm_load(app):
    r = await app.local_ai.warm_load("mock-reasoning")
    assert r["accepted"] is True


@pytest.mark.asyncio
async def test_local_ai_snapshot(app):
    await app.local_ai.warm_load("mock-reasoning")
    snap = app.local_ai.snapshot()
    assert "loaded" in snap
    assert "gpu" in snap


@pytest.mark.asyncio
async def test_local_ai_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        local_ai_enabled=False,
        runtime_enable_background_loops=False,
        model_provider="mock",
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    r = await odin.local_ai.warm_load("mock-reasoning")
    assert r["accepted"] is False
    await odin.shutdown()


def test_inference_channel():
    ev = TraceEvent(kind=TraceEventKind.INFERENCE_STARTED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "models:runtime" in resolve_channels_for_trace(ev)


@pytest.mark.parametrize("i", range(35))
@pytest.mark.asyncio
async def test_ingest_bulk(app, i):
    r = await app.vector_memory.ingest(f"bulk memory document {i} with operational context")
    assert r["accepted"] is True


@pytest.mark.parametrize("i", range(12))
@pytest.mark.asyncio
async def test_search_bulk(app, i):
    await app.vector_memory.ingest(f"indexed content for query {i}")
    results = await app.vector_memory.search(f"query {i}", limit=5)
    assert isinstance(results, list)


@pytest.mark.parametrize("chunk_size", [128, 256, 512, 1024])
def test_chunk_sizes(chunk_size):
    chunks = chunk_with_importance("segment " * 100, chunk_size=chunk_size)
    assert len(chunks) >= 1


@pytest.mark.parametrize("importance", [0.1, 0.3, 0.5, 0.7, 0.9])
@pytest.mark.asyncio
async def test_ingest_importance(app, importance):
    r = await app.vector_memory.ingest("importance weighted memory", metadata={"importance": importance})
    assert r["accepted"] is True


@pytest.mark.parametrize("complexity", [0.1, 0.35, 0.55, 0.75, 0.95])
@pytest.mark.asyncio
async def test_local_ai_route_complexity(app, complexity):
    r = await app.local_ai.route_model(complexity=complexity)
    assert r["profile"]


@pytest.mark.parametrize("template", ["reasoning", "summary", "code"])
@pytest.mark.asyncio
async def test_local_ai_templates(app, template):
    r = await app.local_ai.generate(prompt="template probe", template=template)
    assert r["text"]


@pytest.mark.parametrize("limit", [1, 3, 5, 10])
@pytest.mark.asyncio
async def test_search_limits(app, limit):
    await app.vector_memory.ingest("limit test corpus for retrieval pipeline")
    results = await app.vector_memory.search("corpus", limit=limit)
    assert len(results) <= limit
