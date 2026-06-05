"""Prompt 35 production runtime — memory consolidation tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.streaming.serializers import resolve_channels_for_trace
from odin_backend.core.vector_memory.memory_consolidation import (
    cluster_by_project,
    compress_memories,
    summarize_episodic,
)


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


@pytest.mark.asyncio
async def test_consolidate(app):
    await app.vector_memory.ingest("consolidation probe memory", metadata={"importance": 0.9})
    app.vector_memory.record_episode(event="ingest", context={"source": "test"})
    r = await app.vector_memory.consolidate()
    assert r["accepted"] is True
    assert "compressed" in r
    assert "episodic_summary" in r
    assert "projects" in r


@pytest.mark.asyncio
async def test_consolidate_disabled(tmp_path):
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
    r = await odin.vector_memory.consolidate()
    assert r["accepted"] is False
    await odin.shutdown()


@pytest.mark.asyncio
async def test_compact(app):
    for i in range(60):
        await app.vector_memory.ingest(f"compact cache entry {i}")
    before = app.vector_memory.snapshot()["cache_size"]
    r = await app.vector_memory.compact()
    after = app.vector_memory.snapshot()["cache_size"]
    assert r["evicted"] >= 0
    assert after <= before


@pytest.mark.asyncio
async def test_consolidate_reduces_entries(app):
    for i in range(110):
        app.vector_memory._long_term.store(content=f"entry-{i}", importance=0.1 + (i % 10) / 10.0)
    r = await app.vector_memory.consolidate()
    assert r["compressed"]["compressed"] > 0
    assert app.vector_memory.snapshot()["long_term"] <= 100


def test_compress_memories_unit_no_prune():
    entries = [{"text": f"t{i}", "importance": 0.5} for i in range(50)]
    r = compress_memories(entries, max_entries=100)
    assert r["compressed"] == 0
    assert r["remaining"] == 50


def test_compress_memories_unit_prune():
    entries = [{"text": f"t{i}", "importance": i / 200.0} for i in range(150)]
    r = compress_memories(entries, max_entries=100)
    assert r["compressed"] == 50
    assert r["remaining"] == 100
    assert len(r["entries"]) == 100
    assert r["entries"][0]["importance"] >= r["entries"][-1]["importance"]


def test_summarize_episodic_empty_unit():
    r = summarize_episodic([])
    assert r["count"] == 0
    assert r["summary"] == ""


def test_summarize_episodic_unit():
    episodes = [{"text": f"episode {i}"} for i in range(3)]
    r = summarize_episodic(episodes)
    assert r["count"] == 3
    assert "episode" in r["summary"]


def test_cluster_by_project_unit():
    entries = [
        {"text": "a", "metadata": {"project": "alpha"}},
        {"text": "b", "metadata": {"project": "beta"}},
        {"text": "c"},
    ]
    clusters = cluster_by_project(entries)
    assert "alpha" in clusters
    assert "beta" in clusters
    assert "default" in clusters
    assert len(clusters["alpha"]) == 1


def test_memory_compacted_channel():
    ev = TraceEvent(kind=TraceEventKind.MEMORY_COMPACTED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "memory:runtime" in resolve_channels_for_trace(ev)


@pytest.mark.parametrize("i", range(35))
@pytest.mark.asyncio
async def test_ingest_and_consolidate_bulk(app, i):
    await app.vector_memory.ingest(
        f"bulk memory document {i} for consolidation",
        metadata={"importance": 0.3 + (i % 7) / 10.0, "project": f"proj-{i % 3}"},
    )
    r = await app.vector_memory.consolidate()
    assert r["accepted"] is True


@pytest.mark.parametrize("i", range(15))
@pytest.mark.asyncio
async def test_compact_bulk(app, i):
    await app.vector_memory.ingest(f"compact bulk {i}")
    r = await app.vector_memory.compact()
    assert "evicted" in r


@pytest.mark.parametrize("count", [0, 5, 50, 120, 200])
def test_compress_memories_counts(count):
    entries = [{"text": f"x{i}", "importance": 0.5} for i in range(count)]
    r = compress_memories(entries, max_entries=100)
    assert r["remaining"] <= 100


@pytest.mark.parametrize("i", range(10))
def test_cluster_by_project_bulk(i):
    entries = [{"text": f"t{j}", "metadata": {"project": f"p{j % (i + 1)}"}} for j in range(i + 5)]
    clusters = cluster_by_project(entries)
    assert len(clusters) >= 1


@pytest.mark.parametrize("i", range(8))
@pytest.mark.asyncio
async def test_episode_consolidate_bulk(app, i):
    app.vector_memory.record_episode(event=f"evt-{i}", context={"idx": i})
    r = await app.vector_memory.consolidate()
    assert r["episodic_summary"]["count"] >= 1
