"""Federated memory tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.federated_agents.cross_node_consensus import reach_cross_node_consensus
from odin_backend.core.federated_agents.remote_agent_proxy import RemoteAgentProxy
from odin_backend.core.federated_memory.contradiction_resolution import resolve_contradiction
from odin_backend.core.federated_memory.trust_weighting import weight_by_trust
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.streaming.serializers import resolve_channels_for_trace


@pytest.fixture
def settings(tmp_path):
    db = tmp_path / "fmem.db"
    return Settings(
        database_url=f"sqlite+aiosqlite:///{db.resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        runtime_enable_background_loops=False,
        federation_enabled=True,
        knowledge_fabric_enabled=True,
        world_simulation_enabled=True,
        strategic_reasoning_enabled=True,
        model_provider="mock",
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
async def test_share_memory(app):
    await app.federation_runtime.connect_node(name="peer", mode="trusted_cluster")
    r = await app.federated_memory.share(from_node="local", fact="test fact", confidence=0.8, trust=0.6)
    assert r["accepted"] is True


@pytest.mark.asyncio
async def test_share_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'm.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        federation_enabled=False,
        runtime_enable_background_loops=False,
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    r = await odin.federated_memory.share(from_node="x", fact="f", confidence=0.7, trust=0.9)
    assert r["accepted"] is False
    await odin.shutdown()


@pytest.mark.asyncio
async def test_list_memories(app):
    await app.federated_memory.share(from_node="n1", fact="fact1", confidence=0.7, trust=0.7)
    mems = await app.federated_memory.list_memories()
    assert len(mems) >= 1


@pytest.mark.asyncio
async def test_low_trust_rejected(app):
    r = await app.federated_memory.share(from_node="low", fact="x", confidence=0.5, trust=0.1)
    assert r["accepted"] is False


def test_weight_by_trust():
    w = weight_by_trust(value=0.8, trust=0.6, source_count=2)
    assert 0 < w < 0.8


def test_resolve_contradiction():
    r = resolve_contradiction({"trust": 0.8, "confidence": 0.9}, {"trust": 0.3, "confidence": 0.5})
    assert r["winner"] == "a"


def test_remote_agent_proxy():
    p = RemoteAgentProxy(node_id="n1", agent_id="a1", capabilities=["reason"], expertise=["planning"], trust=0.7, latency_ms=10)
    d = p.to_dict()
    assert d["sandboxed"] is True


@pytest.mark.asyncio
async def test_remote_reasoning(app):
    await app.federation_runtime.connect_node(name="reason-peer", mode="trusted_cluster")
    local = app.federation_runtime.local_node_id
    peers = await app.federation_runtime.list_nodes()
    remote = next(n for n in peers if n["node_id"] != local)
    r = await app.society_federation.delegate_reasoning(to_node=remote["node_id"], query="analyze load")
    assert r["accepted"] is True


@pytest.mark.asyncio
async def test_distributed_delegation(app):
    local = app.federation_runtime.local_node_id
    conn = await app.federation_runtime.connect_node(name="del-peer", mode="trusted_cluster")
    d = app.society_federation.create_delegation(
        from_node=local, to_node=conn["node"]["node_id"], task="analyze", mission_id="m-1"
    )
    assert d["status"] == "active"


def test_cross_node_consensus():
    votes = [{"position": "a", "confidence": 0.8, "trust": 0.7}, {"position": "a", "confidence": 0.75, "trust": 0.6}]
    c = reach_cross_node_consensus(votes)
    assert c["consensus"] is True


@pytest.mark.parametrize("trust", [0.5, 0.6, 0.7, 0.8, 0.9])
@pytest.mark.asyncio
async def test_share_trust_levels(app, trust):
    r = await app.federated_memory.share(from_node="n", fact=f"fact_{trust}", confidence=0.7, trust=trust)
    assert r["accepted"] == (trust >= 0.4)


@pytest.mark.parametrize("i", range(15))
@pytest.mark.asyncio
async def test_multiple_shares(app, i):
    r = await app.federated_memory.share(from_node=f"node_{i}", fact=f"knowledge_{i}", confidence=0.7, trust=0.6)
    assert r["accepted"] is True


def test_knowledge_shared_channel():
    ev = TraceEvent(
        kind=TraceEventKind.KNOWLEDGE_SHARED,
        trace_id="t", span_id="s", causal_chain_id="c", message="share",
    )
    ch = resolve_channels_for_trace(ev)
    assert "federation:runtime" in ch


@pytest.mark.asyncio
async def test_society_federation_snapshot(app):
    snap = app.society_federation.snapshot()
    assert "proxies" in snap


@pytest.mark.asyncio
async def test_federation_dialogue(app):
    local = app.federation_runtime.local_node_id
    conn = await app.federation_runtime.connect_node(name="dlg", mode="trusted_cluster")
    d = app.society_federation.start_dialogue(topic="planning", node_ids=[local, conn["node"]["node_id"]])
    assert d["status"] == "active"
