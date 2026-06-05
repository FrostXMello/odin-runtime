"""WebSocket real-time streaming endpoints."""

from fastapi import APIRouter, Request, WebSocket

from odin_backend.core.streaming.serializers import StreamEnvelope

router = APIRouter(prefix="/ws", tags=["websocket"])


def _odin(websocket: WebSocket):
    return websocket.app.state.odin


def _manager(websocket: WebSocket):
    return _odin(websocket).stream_ws


def _replay_mission(websocket: WebSocket, mission_id: str) -> list[StreamEnvelope]:
    app = _odin(websocket)
    events = app.observability.tracer.store.get_mission_events(mission_id)
    from odin_backend.core.streaming.serializers import envelope_from_trace

    return [envelope_from_trace(e) for e in events[-50:]]


def _replay_task(websocket: WebSocket, task_id: str) -> list[StreamEnvelope]:
    app = _odin(websocket)
    events = app.observability.tracer.store.get_task_events(task_id)
    from odin_backend.core.streaming.serializers import envelope_from_trace

    return [envelope_from_trace(e) for e in events[-50:]]


def _replay_trace(websocket: WebSocket, trace_id: str) -> list[StreamEnvelope]:
    app = _odin(websocket)
    events = app.observability.tracer.store.get_trace_events(trace_id)
    from odin_backend.core.streaming.serializers import envelope_from_trace

    return [envelope_from_trace(e) for e in events[-100:]]


@router.websocket("/runtime")
async def ws_runtime(websocket: WebSocket):
    mgr = _manager(websocket)
    await mgr.handle(websocket, "runtime")


@router.websocket("/missions/{mission_id}")
async def ws_mission(websocket: WebSocket, mission_id: str):
    mgr = _manager(websocket)
    channel = f"mission:{mission_id}"
    replay = _replay_mission(websocket, mission_id)
    await mgr.handle(websocket, channel, replay_recent=replay)


@router.websocket("/tasks/{task_id}")
async def ws_task(websocket: WebSocket, task_id: str):
    mgr = _manager(websocket)
    channel = f"task:{task_id}"
    replay = _replay_task(websocket, task_id)
    await mgr.handle(websocket, channel, replay_recent=replay)


@router.websocket("/executions/{execution_id}")
async def ws_execution(websocket: WebSocket, execution_id: str):
    mgr = _manager(websocket)
    channel = f"execution:{execution_id}"
    await mgr.handle(websocket, channel)


@router.websocket("/traces/{trace_id}")
async def ws_trace(websocket: WebSocket, trace_id: str):
    mgr = _manager(websocket)
    channel = f"trace:{trace_id}"
    replay = _replay_trace(websocket, trace_id)
    await mgr.handle(websocket, channel, replay_recent=replay)


@router.get("/stats")
async def ws_stats(request: Request) -> dict:
    bus = request.app.state.odin.stream_bus
    return {
        "stats": {
            "total_connections": bus.stats.total_connections,
            "channels": bus.stats.channels,
            "events_published": bus.stats.events_published,
            "events_delivered": bus.stats.events_delivered,
            "dropped": bus.stats.dropped,
        }
    }
