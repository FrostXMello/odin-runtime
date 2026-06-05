"""Real-time streaming — event bus, propagation, reconnect semantics."""

import asyncio
import json

import pytest
from fastapi.testclient import TestClient

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.observability.events import TraceEventKind
from odin_backend.core.streaming.event_bus import StreamingEventBus
from odin_backend.core.streaming.serializers import StreamEnvelope, StreamEventKind
from odin_backend.core.streaming.subscriptions import ChannelSpec, channel_matches
from odin_backend.core.streaming.websocket_manager import WebSocketManager


@pytest.mark.asyncio
async def test_channel_matching():
    assert channel_matches(ChannelSpec.parse("runtime"), ["mission:abc", "runtime"])
    assert channel_matches(ChannelSpec.parse("mission:abc"), ["mission:abc"])
    assert not channel_matches(ChannelSpec.parse("mission:xyz"), ["mission:abc"])


@pytest.mark.asyncio
async def test_event_bus_fanout():
    bus = StreamingEventBus()
    q_runtime = await bus.subscribe("runtime")
    q_mission = await bus.subscribe("mission:m1")

    env = StreamEnvelope(
        event_type=StreamEventKind.TASK_STARTED,
        channel="mission:m1",
        mission_id="m1",
        task_id="t1",
        message="test",
    )
    delivered = await bus.publish(env)
    assert delivered >= 2

    got_runtime = await asyncio.wait_for(q_runtime.get(), timeout=1)
    got_mission = await asyncio.wait_for(q_mission.get(), timeout=1)
    assert got_runtime.event_type == StreamEventKind.TASK_STARTED
    assert got_mission.mission_id == "m1"


@pytest.mark.asyncio
async def test_publish_nowait_from_sync():
    bus = StreamingEventBus()
    q = await bus.subscribe("runtime")

    async def waiter():
        return await asyncio.wait_for(q.get(), timeout=2)

    task = asyncio.create_task(waiter())
    await asyncio.sleep(0.05)
    bus.publish_nowait(
        StreamEnvelope(event_type=StreamEventKind.HEARTBEAT, channel="runtime", message="ping")
    )
    msg = await task
    assert msg.event_type == StreamEventKind.HEARTBEAT


@pytest.mark.asyncio
async def test_resubscribe_after_unsubscribe():
    bus = StreamingEventBus()
    q1 = await bus.subscribe("runtime")
    await bus.unsubscribe("runtime", q1)
    q2 = await bus.subscribe("runtime")
    await bus.publish(
        StreamEnvelope(event_type=StreamEventKind.HEALTH_CHANGED, channel="runtime", message="ok")
    )
    msg = await asyncio.wait_for(q2.get(), timeout=1)
    assert msg.event_type == StreamEventKind.HEALTH_CHANGED


@pytest.mark.asyncio
async def test_trace_streams_to_bus():
    from odin_backend.core.observability.hub import ObservabilityHub

    hub = ObservabilityHub()
    q = await hub.stream_bus.subscribe("runtime")
    hub.tracer.record(
        TraceEventKind.MISSION_CREATED,
        message="test stream",
        component="test",
    )
    await asyncio.sleep(0.15)
    env = q.get_nowait()
    assert env.event_type == StreamEventKind.MISSION_CREATED


@pytest.fixture
async def odin_app(tmp_path):
    db_file = tmp_path / "stream_test.db"
    settings = Settings(
        database_url=f"sqlite+aiosqlite:///{db_file.resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        runtime_enable_background_loops=False,
        conscious_loop_enabled=False,
        live_loop_enabled=False,
        stability_loop_enabled=False,
        mission_dispatch_enabled=False,
        mission_gc_enabled=False,
        mission_restore_on_startup=False,
        streaming_enabled=True,
        streaming_heartbeat_interval_seconds=60,
    )
    odin = OdinApplication(settings, use_redis=False)
    await odin.startup()
    yield odin
    await odin.shutdown()


def test_websocket_runtime_receives_publish(odin_app: OdinApplication):
    from fastapi import FastAPI

    from odin_backend.api.routes import ws as ws_routes

    api = FastAPI()
    api.state.odin = odin_app
    api.include_router(ws_routes.router, prefix="/api/v1")

    with TestClient(api) as client:
        with client.websocket_connect("/api/v1/ws/runtime") as ws:
            hello = json.loads(ws.receive_text())
            assert hello["event_type"] == "connected"

            async def publish():
                await odin_app.stream_bus.publish(
                    StreamEnvelope(
                        event_type=StreamEventKind.TASK_STARTED,
                        channel="runtime",
                        message="ws test",
                        task_id="t-ws",
                    )
                )

            asyncio.run(publish())
            for _ in range(10):
                msg = json.loads(ws.receive_text())
                if msg.get("event_type") == "task_started":
                    assert msg["message"] == "ws test"
                    break
            else:
                pytest.fail("expected task_started on websocket")


@pytest.mark.asyncio
async def test_mission_state_changed_bridge(odin_app: OdinApplication):
    from odin_backend.core.streaming.bridge import get_stream_bridge

    bridge = get_stream_bridge()
    assert bridge is not None
    q = await odin_app.stream_bus.subscribe("mission:test-m")
    bridge.mission_state_changed(
        "test-m",
        from_state="queued",
        to_state="running",
        reason="unit",
    )
    await asyncio.sleep(0.1)
    env = await asyncio.wait_for(q.get(), timeout=1)
    assert env.event_type == StreamEventKind.MISSION_STATE_CHANGED
    assert env.payload["to_state"] == "running"
