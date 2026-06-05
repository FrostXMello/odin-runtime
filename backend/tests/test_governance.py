"""Federation governance tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.federation_governance.escalation_rules import should_escalate
from odin_backend.core.federation_governance.permission_matrix import check_permission
from odin_backend.core.federation_governance.trust_engine import TrustEngine
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.streaming.serializers import resolve_channels_for_trace


@pytest.fixture
def settings(tmp_path):
    db = tmp_path / "gov.db"
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
async def test_governance_snapshot(app):
    snap = app.federation_governance.snapshot()
    assert "policies" in snap
    assert len(snap["policies"]) >= 5


@pytest.mark.asyncio
async def test_quarantine_node(app):
    conn = await app.federation_runtime.connect_node(name="bad", mode="trusted_cluster")
    node_id = conn["node"]["node_id"]
    q = app.federation_governance.quarantine(node_id)
    assert q["status"] == "quarantined"
    ok, reason = app.federation_governance.allow_remote_op(node_id, "reason")
    assert ok is False
    assert reason == "node_quarantined"


@pytest.mark.asyncio
async def test_update_trust(app):
    conn = await app.federation_runtime.connect_node(name="trust", mode="trusted_cluster")
    node_id = conn["node"]["node_id"]
    t = app.federation_governance.update_trust(node_id, delta=0.1)
    assert t["trust"] > 0.5


@pytest.mark.asyncio
async def test_permission_denied(app):
    conn = await app.federation_runtime.connect_node(name="perm", mode="trusted_cluster")
    node_id = conn["node"]["node_id"]
    ok, reason = app.federation_governance.allow_remote_op(node_id, "quarantine", level="read")
    assert ok is False
    assert reason == "permission_denied"


def test_check_permission_admin():
    assert check_permission("admin", "quarantine") is True
    assert check_permission("read", "quarantine") is False


def test_trust_engine_bounds():
    te = TrustEngine()
    assert te.score("n1", delta=0.6) == 1.0
    assert te.score("n1", delta=-2.0) == 0.0


def test_should_escalate_quarantine():
    e = should_escalate(trust=0.1, violation_count=3)
    assert e["action"] == "quarantine"


def test_should_escalate_none():
    e = should_escalate(trust=0.8, violation_count=0)
    assert e["escalate"] is False


def test_governance_violation_channel():
    ev = TraceEvent(
        kind=TraceEventKind.GOVERNANCE_VIOLATION,
        trace_id="t", span_id="s", causal_chain_id="c", message="violation",
    )
    ch = resolve_channels_for_trace(ev)
    assert "governance:runtime" in ch


def test_node_quarantined_channel():
    ev = TraceEvent(
        kind=TraceEventKind.NODE_QUARANTINED,
        trace_id="t", span_id="s", causal_chain_id="c", message="q",
    )
    ch = resolve_channels_for_trace(ev)
    assert "governance:runtime" in ch


@pytest.mark.parametrize("level,action,expected", [
    ("none", "read", False),
    ("read", "read", True),
    ("reason", "reason", True),
    ("delegate", "delegate", True),
    ("admin", "admin", True),
])
def test_permission_matrix(level, action, expected):
    assert check_permission(level, action) is expected


@pytest.mark.parametrize("delta", [-0.2, -0.1, 0.0, 0.1, 0.2])
@pytest.mark.asyncio
async def test_trust_deltas(app, delta):
    conn = await app.federation_runtime.connect_node(name=f"t_{delta}", mode="trusted_cluster")
    t = app.federation_governance.update_trust(conn["node"]["node_id"], delta=delta)
    assert 0 <= t["trust"] <= 1


@pytest.mark.parametrize("i", range(10))
@pytest.mark.asyncio
async def test_violation_escalation(app, i):
    conn = await app.federation_runtime.connect_node(name=f"v_{i}", mode="trusted_cluster")
    node_id = conn["node"]["node_id"]
    for _ in range(3):
        app.federation_governance.allow_remote_op(node_id, "admin", level="read")
    snap = app.federation_governance.snapshot()
    assert node_id in snap["quarantined"] or snap["violations"].get(node_id, 0) >= 1


@pytest.mark.asyncio
async def test_audit_records(app):
    conn = await app.federation_runtime.connect_node(name="audit", mode="trusted_cluster")
    app.federation_governance.allow_remote_op(conn["node"]["node_id"], "read", level="admin")
    snap = app.federation_governance.snapshot()
    assert len(snap["audit_recent"]) >= 1


@pytest.mark.asyncio
async def test_emergency_shutdown(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'e.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        federation_enabled=False,
        runtime_enable_background_loops=False,
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    conn = await odin.federation_runtime.connect_node(name="x", mode="trusted_cluster")
    assert conn["accepted"] is False
    await odin.shutdown()
