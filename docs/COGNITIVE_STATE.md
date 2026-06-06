# Cognitive State

`core/cognitive_state/` — global cognitive state estimation.

App handle: `app.cognitive_state`

## Enable

```env
ODIN_COGNITIVE_STATE_ENABLED=1
```

## API

- `GET /api/v1/runtime/cognitive-state`
- `GET /api/v1/runtime/cognitive-state/snapshot`

## Channel

`cognitive-state:runtime`

Tracks cognitive pressure, operator engagement, runtime load, memory saturation, and focus depth.
