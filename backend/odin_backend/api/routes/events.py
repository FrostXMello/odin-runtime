"""SSE event stream."""

import asyncio
import json

from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/stream")
async def event_stream(request: Request):
    app = request.app.state.odin
    hub = app.event_hub

    async def generator():
        queue = hub.subscribe()
        try:
            for event in hub.recent(50):
                yield {"event": event.get("type", "message"), "data": json.dumps(event)}
            while True:
                if await request.is_disconnected():
                    break
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield {"event": event.get("type", "message"), "data": json.dumps(event)}
                except asyncio.TimeoutError:
                    yield {"event": "ping", "data": "{}"}
        finally:
            hub.unsubscribe(queue)

    return EventSourceResponse(generator())
