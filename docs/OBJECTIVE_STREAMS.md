# Objective Streams

`core/objective_streams/` — live objective progression streaming.

App handle: `app.objective_streams`

## Enable

```env
ODIN_OBJECTIVE_STREAMS_ENABLED=1
```

## API

- `GET /api/v1/runtime/objective-streams`
- `POST /api/v1/runtime/objective-streams/stream`
- `POST /api/v1/runtime/objective-streams/reprioritize`

## Channel

`objective-streams:runtime`

## Trace kinds

- `objective_stream_updated`
- `objective_stagnation_detected`

Bounded stream count (max 64). Integrates with `objective_management`.
