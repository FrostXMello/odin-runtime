"""Federation runtime tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.federation.federation_policies import FederationPolicies
from odin_backend.core.federation.federation_topology import FederationTopology
from odin_backend.core.federation.node_identity import NodeIdentity
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.streaming.serializers import resolve_channels_for_trace


@pytest.fixture
def settings(tmp_path):
    db = tmp_path / "fed.db"
    return Settings(
        database_url=f"sqlite+aiosqlite:///{db.resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        runtime_enable_background_loops=False,
        conscious_loop_enabled=False,
        cognitive_learning_enabled=False,
        local_cognition_enabled=True,
        model_provider="mock",
        federation_enabled=True,
        world_simulation_enabled=True,
        strategic_reasoning_enabled=True,
        agent_society_enabled=True,
        knowledge_fabric_enabled=True,
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
async def test_app_has_federation_services(app):
    assert hasattr(app, "federation_runtime")
    assert hasattr(app, "society_federation")
    assert hasattr(app, "world_simulation")
    assert hasattr(app, "strategic_reasoning")
    assert hasattr(app, "federated_memory")
    assert hasattr(app, "federation_governance")


@pytest.mark.asyncio
async def test_local_node_bootstrapped(app):
    assert app.federation_runtime.local_node_id is not None


@pytest.mark.asyncio
async def test_connect_peer_node(app):
    result = await app.federation_runtime.connect_node(name="peer-1", mode="trusted_cluster")
    assert result["accepted"] is True
    assert "node" in result


@pytest.mark.asyncio
async def test_connect_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        runtime_enable_background_loops=False,
        federation_enabled=False,
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    result = await odin.federation_runtime.connect_node(name="x", mode="trusted_cluster")
    assert result["accepted"] is False
    await odin.shutdown()


@pytest.mark.asyncio
async def test_disconnect_node(app):
    conn = await app.federation_runtime.connect_node(name="peer-d", mode="trusted_cluster")
    node_id = conn["node"]["node_id"]
    disc = await app.federation_runtime.disconnect_node(node_id)
    assert disc["status"] == "disconnected"


@pytest.mark.asyncio
async def test_list_nodes(app):
    await app.federation_runtime.connect_node(name="n1", mode="trusted_cluster")
    nodes = await app.federation_runtime.list_nodes()
    assert len(nodes) >= 2


@pytest.mark.asyncio
async def test_topology_snapshot(app):
    await app.federation_runtime.connect_node(name="n2", mode="supervised_mesh")
    topo = app.federation_runtime.topology()
    assert topo["edge_count"] >= 1


@pytest.mark.asyncio
async def test_federation_snapshot(app):
    snap = app.federation_runtime.snapshot()
    assert "mode" in snap
    assert "health" in snap


@pytest.mark.asyncio
async def test_sync_state(app):
    conn = await app.federation_runtime.connect_node(name="sync-node", mode="trusted_cluster")
    synced = await app.federation_runtime.sync_state(conn["node"]["node_id"])
    assert "version" in synced


def test_node_identity_defaults():
    n = NodeIdentity(name="test")
    assert n.role == "worker"
    assert n.federation_mode == "isolated"


def test_topology_valid_modes():
    topo = FederationTopology()
    assert topo.is_valid_mode("trusted_cluster")
    assert not topo.is_valid_mode("internet_open")


@pytest.mark.parametrize("mode", ["trusted_cluster", "supervised_mesh", "research_mesh"])
def test_policies_allow_connect(settings, mode):
    p = FederationPolicies(settings)
    ok, _ = p.allow_connect(mode)
    assert ok is True


def test_policies_isolated_blocked(settings):
    p = FederationPolicies(settings)
    ok, reason = p.allow_connect("isolated")
    assert ok is False
    assert reason == "isolated_mode"


@pytest.mark.parametrize("i", range(15))
@pytest.mark.asyncio
async def test_connect_multiple_nodes(app, i):
    r = await app.federation_runtime.connect_node(name=f"node_{i}", mode="trusted_cluster")
    assert r["accepted"] is True


@pytest.mark.parametrize("mode", ["trusted_cluster", "supervised_mesh", "research_mesh"])
@pytest.mark.asyncio
async def test_connect_modes(app, mode):
    r = await app.federation_runtime.connect_node(name=f"m_{mode}", mode=mode)
    assert r["accepted"] is True


def test_federation_trace_channels():
    ev = TraceEvent(
        kind=TraceEventKind.FEDERATION_NODE_CONNECTED,
        trace_id="t", span_id="s", causal_chain_id="c", message="connect",
    )
    ch = resolve_channels_for_trace(ev)
    assert "federation:runtime" in ch


def test_remote_reasoning_trace_channels():
    ev = TraceEvent(
        kind=TraceEventKind.REMOTE_REASONING_COMPLETED,
        trace_id="t", span_id="s", causal_chain_id="c", message="done",
    )
    ch = resolve_channels_for_trace(ev)
    assert "federation:runtime" in ch


@pytest.mark.parametrize("name", ["alpha", "beta", "gamma", "delta"])
@pytest.mark.asyncio
async def test_node_names(app, name):
    r = await app.federation_runtime.connect_node(name=name, mode="trusted_cluster")
    assert r["node"]["name"] == name


@pytest.mark.asyncio
async def test_presence_heartbeat(app):
    snap = app.federation_runtime.snapshot()
    assert snap["presence"]["nodes_online"] >= 1


@pytest.mark.asyncio
async def test_health_monitoring(app):
    await app.federation_runtime.connect_node(name="healthy", mode="trusted_cluster")
    health = app.federation_runtime.snapshot()["health"]
    assert health["nodes_checked"] >= 1


@pytest.mark.parametrize("role", ["worker", "coordinator", "research", "executor"])
@pytest.mark.asyncio
async def test_connect_roles(app, role):
    r = await app.federation_runtime.connect_node(name=f"r_{role}", role=role, mode="trusted_cluster")
    assert r["accepted"] is True
    assert r["node"]["role"] == role


@pytest.mark.asyncio
async def test_society_federation_proxies(app):
    from odin_backend.core.federated_agents.remote_agent_proxy import RemoteAgentProxy

    proxy = RemoteAgentProxy(
        node_id="remote-1", agent_id="agent-1", capabilities=["plan"],
        expertise=["infra"], trust=0.7, latency_ms=12,
    )
    registered = app.society_federation.register_proxy(proxy)
    assert registered["sandboxed"] is True
    assert len(app.society_federation.list_proxies()) >= 1


@pytest.mark.asyncio
async def test_federation_max_nodes_respected(settings, tmp_path):
    s = Settings(
        database_url=settings.database_url,
        chroma_persist_dir=tmp_path / "chroma2",
        sandbox_work_dir=tmp_path / "sandbox2",
        runtime_enable_background_loops=False,
        federation_enabled=True,
        federation_max_nodes=3,
        model_provider="mock",
        queue_persist_enabled=False,
        async_mission_runtime_enabled=False,
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    for i in range(5):
        await odin.federation_runtime.connect_node(name=f"max_{i}", mode="trusted_cluster")
    nodes = await odin.federation_runtime.list_nodes()
    assert len(nodes) >= 1
    await odin.shutdown()
