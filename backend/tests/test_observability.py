"""Observability — trace propagation, timelines, diagnostics, signal lineage."""

import asyncio

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.observability.context import (
    CausalTraceContext,
    bind_context,
    current_context,
    reset_context,
)
from odin_backend.core.observability.events import TraceEventKind
from odin_backend.core.observability.hub import ObservabilityHub
from odin_backend.core.observability.timeline import build_mission_timeline, build_task_timeline
from odin_backend.core.observability.diagnostics import analyze_runtime
from odin_backend.models.mission import MissionLifecycle


@pytest.fixture
async def app(tmp_path):
    db_file = tmp_path / "odin_test.db"
    settings = Settings(
        database_url=f"sqlite+aiosqlite:///{db_file.resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        runtime_enable_background_loops=False,
        conscious_loop_enabled=False,
        live_loop_enabled=False,
        stability_loop_enabled=False,
        mission_worker_enabled=False,
        mission_dispatch_enabled=False,
        mission_gc_enabled=False,
        mission_restore_on_startup=False,
    )
    odin = OdinApplication(settings, use_redis=False)
    await odin.startup()
    yield odin
    await odin.shutdown()


def test_trace_context_async_propagation():
    ctx = CausalTraceContext(mission_id="m1")
    token = bind_context(ctx)

    async def inner():
        got = current_context()
        assert got is not None
        assert got.trace_id == ctx.trace_id
        assert got.mission_id == "m1"

    asyncio.run(inner())
    reset_context(token)
    assert current_context() is None


def test_child_span_preserves_causal_chain():
    parent = CausalTraceContext(trace_id="t1", causal_chain_id="chain-1")
    child = parent.child_span(task_id="task-1")
    assert child.trace_id == "t1"
    assert child.parent_span_id == parent.span_id
    assert child.causal_chain_id == "chain-1"
    assert child.task_id == "task-1"


@pytest.mark.asyncio
async def test_mission_trace_propagation(app: OdinApplication):
    mission = await app.mission_manager.create("Observability trace step one.")
    assert mission.metadata.get("trace_id")
    assert mission.metadata.get("causal_chain_id")
    events = app.observability.tracer.store.get_mission_events(mission.mission_id)
    kinds = {e.kind for e in events}
    assert TraceEventKind.MISSION_CREATED in kinds


@pytest.mark.asyncio
async def test_timeline_sorted_entries(app: OdinApplication):
    mission = await app.mission_manager.create("Timeline alpha. Timeline beta.")
    await app.mission_dispatcher.dispatch_mission_now(mission.mission_id)
    mission = await app.mission_manager.get(mission.mission_id)
    events = app.observability.tracer.store.get_mission_events(mission.mission_id)
    timeline = build_mission_timeline(mission, events)
    entries = timeline["entries"]
    assert len(entries) >= 1
    keys = [e["sort_key"] for e in entries]
    assert keys == sorted(keys)


@pytest.mark.asyncio
async def test_task_timeline(app: OdinApplication):
    mission = await app.mission_manager.create("Task timeline step one. Task timeline step two.")
    task_id = list(mission.task_graph.nodes.keys())[0]
    await app.mission_runtime.run_wave(app, mission)
    events = app.observability.tracer.store.get_task_events(task_id)
    tl = build_task_timeline(mission, task_id, events)
    assert tl["task_id"] == task_id


@pytest.mark.asyncio
async def test_policy_blocked_trace(app: OdinApplication):
    mission = await app.mission_manager.create("Delete production database", human_approved=False)
    assert mission.current_state == MissionLifecycle.APPROVAL_REQUIRED
    events = app.observability.tracer.store.get_mission_events(mission.mission_id)
    assert any(e.kind == TraceEventKind.POLICY_BLOCKED for e in events)


@pytest.mark.asyncio
async def test_get_trace_by_id(app: OdinApplication):
    mission = await app.mission_manager.create("Trace lookup step.")
    trace_id = mission.metadata["trace_id"]
    data = app.observability.tracer.get_trace(trace_id)
    assert data["trace_id"] == trace_id
    assert data["event_count"] >= 1


@pytest.mark.asyncio
async def test_root_cause_diagnostics(app: OdinApplication):
    report = analyze_runtime(app)
    assert report.status in ("healthy", "degraded", "critical")
    assert isinstance(report.findings, list)


@pytest.mark.asyncio
async def test_signal_graph_records(app: OdinApplication):
    from odin_backend.core.bus.signals import Signal, SignalKind
    from odin_backend.models.event import Event, EventType
    from odin_backend.models.task import AgentId

    event = Event(type=EventType.TASK_CREATED, source=AgentId.ODIN, payload={"test": True})
    await app.event_bus.publish_internal(event)
    graph = app.observability.signal_graph.export_graph(limit_edges=50)
    assert "nodes" in graph.model_dump()


def test_memory_mutation_audit():
    hub = ObservabilityHub()
    ctx = CausalTraceContext(mission_id="m-test")
    bind_context(ctx)
    rec = hub.memory_audit.record(
        actor="test",
        reason="unit_test",
        category="episodic",
        new_value="hello",
        mission_id="m-test",
    )
    assert rec.new_hash
    assert rec.trace_id == ctx.trace_id
