# Rollback Intelligence

`core/rollback_intelligence/` — rollback graph generation and execution replay analysis.

App handle: `app.rollback_intelligence`

## Enable

```env
ODIN_ROLLBACK_INTELLIGENCE_ENABLED=1
```

## API

- `GET /api/v1/runtime/rollback-intelligence/graph`
- `POST /api/v1/runtime/rollback-intelligence/replay`
- `GET /api/v1/runtime/rollback-replay`

## Channel

`rollback-intelligence:runtime`

## Trace kinds

- `rollback_graph_generated`
- `rollback_confidence_estimated`
- `execution_window_replayed`

SQLite rollback registry (600 node cap). Bounded replay loops (max 40). Approval-gated rollback selection.
