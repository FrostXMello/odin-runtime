"""Prompt 13 — runtime signal isolation and recursion protection."""

import asyncio

import pytest
from httpx import ASGITransport, AsyncClient

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.bus.signals import SignalOrigin, is_kernel_eligible, origin_from_event
from odin_backend.core.bus.unified_bus import SignalUnificationBus
from odin_backend.core.runtime.recursion_guard import RecursionGuard, RecursionGuardDecision
from odin_backend.events.bus import InMemoryEventBus
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId


@pytest.fixture
async def app():
    settings = Settings(
        runtime_enable_background_loops=False,
        conscious_loop_enabled=False,
        live_loop_enabled=False,
        stability_loop_enabled=False,
    )
    odin = OdinApplication(settings, use_redis=False)
    await odin.startup()
    yield odin
    await odin.shutdown()


@pytest.mark.asyncio
async def test_internal_events_bypass_kernel(app: OdinApplication):
    bus = app.event_bus
    assert isinstance(bus, SignalUnificationBus)
    before_kernel = bus.runtime_metrics()["kernel_processed"]
    before_bypass = bus.runtime_metrics()["internal_bypassed"]

    for _ in range(20):
        await bus.publish_internal(
            Event(type=EventType.COGNITION_PROGRESS, source=AgentId.ODIN, payload={"n": _})
        )

    metrics = bus.runtime_metrics()
    assert metrics["internal_bypassed"] >= before_bypass + 20
    assert metrics["kernel_processed"] == before_kernel


@pytest.mark.asyncio
async def test_external_events_process_kernel(app: OdinApplication):
    bus = app.event_bus
    before = app.kernel.get_state().signal_count
    await bus.publish_external(
        Event(
            type=EventType.WORKFLOW_COMPLETED,
            source=AgentId.ODIN,
            workflow_id="wf-stability-1",
            payload={"status": "done"},
        )
    )
    after = app.kernel.get_state().signal_count
    assert after > before


@pytest.mark.asyncio
async def test_no_recursive_kernel_loop_under_internal_flood(app: OdinApplication):
    bus = app.event_bus
    before = app.kernel.get_state().signal_count

    async def flood():
        for i in range(200):
            await bus.publish_internal(
                Event(
                    type=EventType.RUNTIME_HEARTBEAT,
                    source=AgentId.ODIN,
                    payload={"i": i},
                )
            )

    await asyncio.gather(flood(), flood())

    after = app.kernel.get_state().signal_count
    assert after == before


@pytest.mark.asyncio
async def test_recursion_guard_suppresses_loops():
    guard = RecursionGuard(max_repeats=3, loop_window_seconds=10.0)
    from odin_backend.core.bus.signals import Signal

    signal = Signal(
        origin=SignalOrigin.EXTERNAL,
        type="cognition.shift",
        name="cognition.shift",
        correlation_id="loop-1",
    )
    decisions = [guard.evaluate(signal, eligible_for_kernel=True).decision for _ in range(8)]
    assert RecursionGuardDecision.SUPPRESS in decisions
    assert guard.metrics.suppressed_signal_count >= 1


@pytest.mark.asyncio
async def test_origin_classification():
    internal = origin_from_event(
        Event(type=EventType.KERNEL_STATE_UPDATED, source=AgentId.ODIN, payload={})
    )
    assert internal == SignalOrigin.KERNEL_INTERNAL
    assert not is_kernel_eligible(internal)

    external = origin_from_event(
        Event(type=EventType.CONVERSATION_MESSAGE, source=AgentId.ODIN, payload={})
    )
    assert external == SignalOrigin.EXTERNAL
    assert is_kernel_eligible(external)


@pytest.mark.asyncio
async def test_stability_loop_does_not_increment_kernel(app: OdinApplication):
    before = app.kernel.get_state().signal_count
    await app.stability.run_cycle(app)
    after = app.kernel.get_state().signal_count
    assert after == before


@pytest.mark.asyncio
async def test_runtime_diagnostics_api(app: OdinApplication):
    from fastapi import FastAPI
    from odin_backend.api.routes import runtime_diagnostics

    api = FastAPI()
    api.state.odin = app
    api.include_router(runtime_diagnostics.router, prefix="/api/v1")
    transport = ASGITransport(app=api)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        health = await client.get("/api/v1/runtime/health")
        recursion = await client.get("/api/v1/runtime/recursion")
        signals = await client.get("/api/v1/runtime/signals")

    assert health.status_code == 200
    assert recursion.status_code == 200
    assert signals.status_code == 200
    assert "runtime_loop_health" in health.json()
    assert recursion.json()["guard_enabled"] is True
    assert "throughput" in signals.json()


@pytest.mark.asyncio
async def test_cognitive_state_runtime_metrics(app: OdinApplication):
    bus = app.event_bus
    await bus.publish_external(
        Event(
            type=EventType.TASK_CREATED,
            source=AgentId.ODIN,
            task_id="t-1",
            payload={"goal": "test"},
        )
    )
    state = app.kernel.get_state()
    assert state.runtime_loop_health in ("healthy", "degraded", "critical")
    assert state.kernel_processing_rate >= 0.0
