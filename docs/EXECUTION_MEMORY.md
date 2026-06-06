# Execution Memory

`core/execution_memory/` — execution history persistence.

App handle: `app.execution_memory`

## Enable

```env
ODIN_EXECUTION_MEMORY_ENABLED=1
```

## API

- `GET /api/v1/runtime/execution-memory/history`
- `POST /api/v1/runtime/execution-memory/persist`
- `POST /api/v1/runtime/execution-memory/replay`

## Channel

`execution-memory:runtime`

## Trace kinds

- `execution_chain_persisted`

SQLite-backed registry (max 250 chains). Lazy replay hydration. Execution compression.
