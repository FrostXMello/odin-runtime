"""Runtime continuity tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.runtime_continuity.cognition_resume import CognitionResume
from odin_backend.core.runtime_continuity.operator_identity import OperatorIdentity
from odin_backend.core.streaming.serializers import resolve_channels_for_trace


@pytest.fixture
def settings(tmp_path):
    db = tmp_path / "cont.db"
    return Settings(
        database_url=f"sqlite+aiosqlite:///{db.resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        runtime_enable_background_loops=False,
        runtime_continuity_enabled=True,
        background_cognition_enabled=True,
        runtime_evolution_enabled=True,
        cognitive_economy_enabled=True,
        meta_reasoning_enabled=True,
        operational_planning_enabled=True,
        operator_relationship_enabled=True,
        distributed_optimization_enabled=True,
        federation_enabled=True,
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
async def test_has_continuity_runtime(app):
    assert hasattr(app, "continuity_runtime")


@pytest.mark.asyncio
async def test_checkpoint(app):
    snap = await app.continuity_runtime.checkpoint(state={"missions": 1})
    assert "snapshot_id" in snap or "kind" in snap


@pytest.mark.asyncio
async def test_defer_reasoning(app):
    d = await app.continuity_runtime.defer_reasoning(kind="investigation", payload={"topic": "x"})
    assert d["status"] == "deferred"


@pytest.mark.asyncio
async def test_continuity_snapshot(app):
    snap = await app.continuity_runtime.snapshot()
    assert "operator" in snap


@pytest.mark.asyncio
async def test_mission_continuity(app):
    await app.continuity_runtime.defer_reasoning(kind="task", payload={"mission_id": "m-1"})
    m = app.continuity_runtime.missions_for("m-1")
    assert m["mission_id"] == "m-1"


def test_operator_identity():
    o = OperatorIdentity(name="test")
    assert o.collaboration_style == "balanced"


def test_cognition_resume():
    r = CognitionResume()
    r.defer(kind="a", payload={})
    assert len(r.pending()) == 1
    resumed = r.resume_all()
    assert len(resumed) == 1


def test_continuity_channel():
    ev = TraceEvent(kind=TraceEventKind.CONTINUITY_RESTORED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "continuity:runtime" in resolve_channels_for_trace(ev)


@pytest.mark.parametrize("i", range(25))
@pytest.mark.asyncio
async def test_checkpoints(app, i):
    snap = await app.continuity_runtime.checkpoint(state={"index": i})
    assert snap is not None


@pytest.mark.parametrize("kind", ["investigation", "planning", "review", "analysis"])
@pytest.mark.asyncio
async def test_defer_kinds(app, kind):
    d = await app.continuity_runtime.defer_reasoning(kind=kind, payload={"k": kind})
    assert d["kind"] == kind


@pytest.mark.parametrize("mid", [f"mission-{i}" for i in range(10)])
@pytest.mark.asyncio
async def test_mission_deferred(app, mid):
    await app.continuity_runtime.defer_reasoning(kind="m", payload={"mission_id": mid})
    assert len(app.continuity_runtime.missions_for(mid)["deferred"]) >= 1
