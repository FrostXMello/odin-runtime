# Runtime Execution Visibility

`core/runtime_execution_visibility/` — live execution visualization.

App handle: `app.runtime_execution_visibility`

## Enable

```env
ODIN_RUNTIME_EXECUTION_VISIBILITY_ENABLED=1
ODIN_EXECUTION_STREAM_DENSITY=balanced
```

## API

- `GET /api/v1/runtime/execution-visibility/heatmap`
- `GET /api/v1/runtime/execution-pressure`

## Channel

`execution-visibility:runtime`

## Trace kinds

- `execution_visibility_streamed`
- `execution_pressure_updated`

Adaptive execution throttling. Stream compression. Bounded streams (max 56).
