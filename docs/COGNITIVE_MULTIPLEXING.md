# Cognitive Multiplexing

`core/cognitive_multiplexing/` — unified cognition streams and runtime multiplexing.

App handle: `app.cognitive_multiplexing`

## Enable

```env
ODIN_COGNITIVE_MULTIPLEXING_ENABLED=1
ODIN_COGNITION_MULTIPLEX_MODE=adaptive
```

## API

- `GET /api/v1/runtime/cognitive-multiplexing`
- `POST /api/v1/runtime/cognitive-multiplexing/multiplex`
- `POST /api/v1/runtime/cognitive-multiplexing/compress`

## Channel

`cognitive-multiplexing:runtime`

## Trace kinds

- `cognition_streams_multiplexed`
- `runtime_streams_compressed`

Integrates with `realtime_coordination`, `runtime_fusion`.

Bounded multiplex loops (max 64). Stream compression for low-power mode. Adaptive cognition density.
