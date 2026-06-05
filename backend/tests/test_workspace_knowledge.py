"""Prompt 36 production runtime — workspace knowledge tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.streaming.serializers import resolve_channels_for_trace
from odin_backend.core.workspace_knowledge.personal_knowledge_graph import PersonalKnowledgeGraph
from odin_backend.core.workspace_knowledge.semantic_workspace import SemanticWorkspace


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
async def test_app_has_workspace_knowledge(app):
    assert hasattr(app, "workspace_knowledge")


@pytest.mark.asyncio
async def test_ingest(app):
    r = await app.workspace_knowledge.ingest(title="Meeting notes", content="Discussed roadmap priorities")
    assert r["accepted"] is True
    assert r["document"]["title"] == "Meeting notes"
    assert "chunk" in r


@pytest.mark.asyncio
async def test_ingest_pdf(app):
    r = await app.workspace_knowledge.ingest_pdf(filename="spec.pdf", text="PDF specification content for search")
    assert r["accepted"] is True
    assert r["document"]["title"] == "spec.pdf"


@pytest.mark.asyncio
async def test_search(app):
    await app.workspace_knowledge.ingest(title="Search doc", content="kubernetes deployment guide")
    hits = await app.workspace_knowledge.search("kubernetes", limit=5)
    assert isinstance(hits, list)
    assert len(hits) >= 1


@pytest.mark.asyncio
async def test_timeline(app):
    await app.workspace_knowledge.ingest(title="Event A", content="alpha")
    await app.workspace_knowledge.ingest(title="Event B", content="beta")
    tl = app.workspace_knowledge.timeline()
    assert isinstance(tl, list)
    assert len(tl) >= 2


@pytest.mark.asyncio
async def test_snapshot(app):
    await app.workspace_knowledge.ingest(title="Snap", content="snapshot probe")
    snap = app.workspace_knowledge.snapshot()
    assert snap["documents"] >= 1
    assert "graph" in snap


@pytest.mark.asyncio
async def test_ingest_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        workspace_knowledge_enabled=False,
        runtime_enable_background_loops=False,
        model_provider="mock",
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    r = await odin.workspace_knowledge.ingest(title="blocked", content="blocked")
    assert r["accepted"] is False
    assert r["reason"] == "workspace_knowledge_disabled"
    await odin.shutdown()


def test_semantic_workspace_index_search():
    ws = SemanticWorkspace()
    ws.index(text="python async patterns", metadata={"kind": "note"})
    hits = ws.search("python", limit=3)
    assert len(hits) == 1
    assert "python" in hits[0]["text"]


def test_semantic_workspace_no_match():
    ws = SemanticWorkspace()
    ws.index(text="rust ownership", metadata={})
    assert ws.search("python") == []


def test_personal_knowledge_graph_add_snapshot():
    graph = PersonalKnowledgeGraph()
    node = graph.add_node("n1", label="Architecture", kind="note")
    assert node["label"] == "Architecture"
    snap = graph.snapshot()
    assert snap["nodes"] == 1
    assert snap["sample"][0]["id"] == "n1"


def test_personal_knowledge_graph_multiple_nodes():
    graph = PersonalKnowledgeGraph()
    for i in range(8):
        graph.add_node(f"n{i}", label=f"L{i}", kind="note")
    assert graph.snapshot()["nodes"] == 8


def test_knowledge_cluster_created_channel():
    ev = TraceEvent(kind=TraceEventKind.KNOWLEDGE_CLUSTER_CREATED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "workspace:runtime" in resolve_channels_for_trace(ev)


@pytest.mark.parametrize("i", range(35))
@pytest.mark.asyncio
async def test_ingest_bulk(app, i):
    r = await app.workspace_knowledge.ingest(title=f"doc-{i}", content=f"content bulk {i} searchable")
    assert r["accepted"] is True


@pytest.mark.parametrize("i", range(25))
@pytest.mark.asyncio
async def test_ingest_pdf_bulk(app, i):
    r = await app.workspace_knowledge.ingest_pdf(filename=f"file-{i}.pdf", text=f"pdf text {i} keyword")
    assert r["accepted"] is True


@pytest.mark.parametrize("i", range(20))
@pytest.mark.asyncio
async def test_search_bulk(app, i):
    await app.workspace_knowledge.ingest(title=f"search-{i}", content=f"findme-{i} unique token")
    hits = await app.workspace_knowledge.search(f"findme-{i}", limit=3)
    assert isinstance(hits, list)


@pytest.mark.parametrize("i", range(15))
@pytest.mark.asyncio
async def test_timeline_bulk(app, i):
    await app.workspace_knowledge.ingest(title=f"tl-{i}", content=f"timeline entry {i}")
    tl = app.workspace_knowledge.timeline()
    assert len(tl) >= 1


@pytest.mark.parametrize(
    "kind",
    ["note", "doc", "reference", "meeting", "idea", "note", "doc", "reference", "meeting", "idea"],
)
@pytest.mark.asyncio
async def test_ingest_kinds(app, kind):
    r = await app.workspace_knowledge.ingest(title=f"{kind}-title", content=f"{kind} body", kind=kind)
    assert r["accepted"] is True
