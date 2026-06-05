"""Prompt 36 production runtime — storage optimization tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.storage_optimization.archive_runtime import archive_entries
from odin_backend.core.storage_optimization.embedding_cache import EmbeddingCache
from odin_backend.core.storage_optimization.semantic_compaction import compact_chunks
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
        runtime_guardian_enabled=True,
        self_healing_enabled=True,
        real_automation_enabled=True,
        memory_consolidation_enabled=True,
        survival_mode="balanced",
        queue_persist_enabled=False,
        async_mission_runtime_enabled=False,
        project_os_enabled=True,
        developer_integrations_enabled=True,
        workspace_knowledge_enabled=True,
        productivity_enabled=True,
        local_search_enabled=True,
        communications_enabled=True,
        storage_optimization_enabled=True,
    )


@pytest.fixture
async def app(settings):
    odin = OdinApplication(settings, use_redis=False)
    await odin.startup()
    yield odin
    await odin.shutdown()


@pytest.mark.asyncio
async def test_app_has_storage_optimization(app):
    assert hasattr(app, "storage_optimization")


@pytest.mark.asyncio
async def test_optimize(app):
    await app.vector_memory.ingest("storage optimize probe")
    r = await app.storage_optimization.optimize()
    assert r["accepted"] is True
    assert "cache_size" in r
    assert "acceleration" in r


@pytest.mark.asyncio
async def test_archive(app):
    entries = [{"id": f"e{i}", "content": f"data-{i}"} for i in range(5)]
    r = await app.storage_optimization.archive(entries)
    assert r["accepted"] is True
    assert r["archived"] == 0
    assert r["remaining"] == 5


@pytest.mark.asyncio
async def test_archive_large(app):
    entries = [{"id": f"e{i}"} for i in range(150)]
    r = await app.storage_optimization.archive(entries)
    assert r["accepted"] is True
    assert r["archived"] == 50
    assert r["remaining"] == 100


@pytest.mark.asyncio
async def test_snapshot(app):
    await app.storage_optimization.optimize()
    snap = app.storage_optimization.snapshot()
    assert "cache_size" in snap
    assert "cold_storage" in snap


@pytest.mark.asyncio
async def test_optimize_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        storage_optimization_enabled=False,
        runtime_enable_background_loops=False,
        model_provider="mock",
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    r = await odin.storage_optimization.optimize()
    assert r["accepted"] is False
    assert r["reason"] == "storage_optimization_disabled"
    await odin.shutdown()


def test_embedding_cache_put_get():
    cache = EmbeddingCache(max_entries=3)
    cache.put("a", [0.1, 0.2])
    assert cache.get("a") == [0.1, 0.2]
    assert cache.size() == 1


def test_embedding_cache_eviction():
    cache = EmbeddingCache(max_entries=2)
    cache.put("a", [1.0])
    cache.put("b", [2.0])
    cache.put("c", [3.0])
    assert cache.size() == 2
    assert cache.get("a") is None


def test_semantic_compaction_noop():
    chunks = [{"text": "a", "importance": 0.5}]
    result = compact_chunks(chunks, target=50)
    assert result["compacted"] == 0
    assert len(result["chunks"]) == 1


def test_semantic_compaction_reduces():
    chunks = [{"text": f"c{i}", "importance": i / 100} for i in range(80)]
    result = compact_chunks(chunks, target=50)
    assert result["compacted"] == 30
    assert len(result["chunks"]) == 50


def test_archive_entries_unit():
    entries = [{"id": str(i)} for i in range(120)]
    result = archive_entries(entries, keep=100)
    assert result["archived"] == 20
    assert result["remaining"] == 100


def test_archive_entries_small():
    entries = [{"id": "1"}, {"id": "2"}]
    result = archive_entries(entries)
    assert result["archived"] == 0
    assert result["remaining"] == 2


def test_retrieval_optimized_channel():
    ev = TraceEvent(kind=TraceEventKind.RETRIEVAL_OPTIMIZED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "storage:runtime" in resolve_channels_for_trace(ev)


@pytest.mark.parametrize("i", range(35))
@pytest.mark.asyncio
async def test_optimize_bulk(app, i):
    await app.vector_memory.ingest(f"optimize bulk {i}")
    r = await app.storage_optimization.optimize()
    assert r["accepted"] is True


@pytest.mark.parametrize("i", range(25))
@pytest.mark.asyncio
async def test_archive_bulk(app, i):
    count = 10 + (i % 5)
    entries = [{"id": f"bulk-{i}-{j}"} for j in range(count)]
    r = await app.storage_optimization.archive(entries)
    assert r["accepted"] is True


@pytest.mark.parametrize("i", range(20))
@pytest.mark.asyncio
async def test_snapshot_bulk(app, i):
    await app.storage_optimization.optimize()
    snap = app.storage_optimization.snapshot()
    assert snap["cache_size"] >= 0


@pytest.mark.parametrize("target", [10, 25, 50, 75, 100])
def test_compaction_targets(target):
    chunks = [{"text": f"x{n}", "importance": n / 200} for n in range(120)]
    result = compact_chunks(chunks, target=target)
    assert len(result["chunks"]) == target
    assert result["compacted"] == 120 - target


@pytest.mark.parametrize(
    "keep",
    [50, 75, 100, 125, 150, 50, 75, 100, 125, 150],
)
def test_archive_keep_levels(keep):
    entries = [{"id": str(i)} for i in range(200)]
    result = archive_entries(entries, keep=keep)
    assert result["archived"] == 200 - keep
    assert result["remaining"] == keep
