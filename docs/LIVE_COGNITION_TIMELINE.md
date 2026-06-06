# Live Cognition Timeline

`core/live_cognition_timeline/` — unified cognition playback and mission timeline rendering.

App handle: `app.live_cognition_timeline`

## Enable

```env
ODIN_LIVE_COGNITION_TIMELINE_ENABLED=1
```

## API

- `GET /api/v1/runtime/live-cognition-timeline`
- `POST /api/v1/runtime/live-cognition-timeline/replay`
- `POST /api/v1/runtime/live-cognition-timeline/append`
- `GET /api/v1/runtime/cognition-replay`

## Channel

`live-cognition-timeline:runtime`

## Trace kinds

- `cognition_timeline_appended`
- `cognition_window_replayed`

SQLite-backed cognition timeline registry (max 500 events). Bounded replay loops (max 40). Overnight timeline compression.
