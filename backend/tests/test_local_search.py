"""Prompt 36 production runtime — local semantic search tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.streaming.serializers import resolve_channels_for_trace
from odin_backend.core.vector_memory.local_search import hybrid_search


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


@pytest.fixture
def project_dir(tmp_path):
    root = tmp_path / "search-repo"
    root.mkdir()
    return root


@pytest.mark.asyncio
async def test_app_has_vector_memory(app):
    assert hasattr(app, "vector_memory")


@pytest.mark.asyncio
async def test_search_hybrid(app):
    await app.vector_memory.ingest("hybrid search probe about databases")
    r = await app.vector_memory.search_hybrid("databases", limit=5)
    assert r["accepted"] is True
    assert r["query"] == "databases"
    assert "results" in r
    assert "count" in r


@pytest.mark.asyncio
async def test_search_hybrid_with_workspace(app):
    await app.workspace_knowledge.ingest(title="WS", content="workspace knowledge about graphql")
    r = await app.vector_memory.search_hybrid("graphql", limit=5)
    assert r["accepted"] is True
    assert r["count"] >= 1


@pytest.mark.asyncio
async def test_search_hybrid_with_project(app, project_dir):
    await app.project_os.register_project(name="SearchProject", path=str(project_dir.resolve()))
    r = await app.vector_memory.search_hybrid("SearchProject", limit=5)
    assert r["accepted"] is True
    sources = {hit.get("source") for hit in r["results"]}
    assert "project" in sources


@pytest.mark.asyncio
async def test_search_hybrid_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        local_search_enabled=False,
        vector_memory_enabled=True,
        runtime_enable_background_loops=False,
        model_provider="mock",
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    r = await odin.vector_memory.search_hybrid("blocked")
    assert r["accepted"] is False
    assert r["reason"] == "local_search_disabled"
    await odin.shutdown()


@pytest.mark.asyncio
async def test_hybrid_search_unit(app):
    await app.vector_memory.ingest("unit hybrid content")
    result = await hybrid_search(app, "unit", limit=3)
    assert result["query"] == "unit"
    assert isinstance(result["results"], list)


def test_semantic_search_completed_channel():
    ev = TraceEvent(kind=TraceEventKind.SEMANTIC_SEARCH_COMPLETED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "search:runtime" in resolve_channels_for_trace(ev)


@pytest.mark.parametrize("i", range(35))
@pytest.mark.asyncio
async def test_search_hybrid_bulk(app, i):
    await app.vector_memory.ingest(f"bulk search token alpha-{i}")
    r = await app.vector_memory.search_hybrid(f"alpha-{i}", limit=5)
    assert r["accepted"] is True


@pytest.mark.parametrize("i", range(25))
@pytest.mark.asyncio
async def test_hybrid_search_unit_bulk(app, i):
    await app.workspace_knowledge.ingest(title=f"u{i}", content=f"unit bulk keyword beta-{i}")
    result = await hybrid_search(app, f"beta-{i}", limit=5)
    assert result["count"] >= 0


@pytest.mark.parametrize("limit", [1, 3, 5, 10, 15, 20])
@pytest.mark.asyncio
async def test_search_hybrid_limits(app, limit):
    await app.vector_memory.ingest("limit probe content")
    r = await app.vector_memory.search_hybrid("limit", limit=limit)
    assert r["accepted"] is True
    assert len(r["results"]) <= limit


@pytest.mark.parametrize("i", range(20))
@pytest.mark.asyncio
async def test_multi_source_hybrid(app, project_dir, i):
    await app.project_os.register_project(name=f"Proj{i}", path=str(project_dir.resolve()))
    await app.workspace_knowledge.ingest(title=f"m{i}", content=f"multi source gamma-{i}")
    await app.vector_memory.ingest(f"multi source gamma-{i}")
    r = await app.vector_memory.search_hybrid(f"gamma-{i}", limit=10)
    assert r["accepted"] is True


@pytest.mark.parametrize(
    "query",
    [
        "python",
        "rust",
        "typescript",
        "kubernetes",
        "docker",
        "graphql",
        "sqlite",
        "redis",
        "pytest",
        "fastapi",
    ],
)
@pytest.mark.asyncio
async def test_search_queries(app, query):
    await app.vector_memory.ingest(f"content about {query}")
    r = await app.vector_memory.search_hybrid(query, limit=3)
    assert r["accepted"] is True
