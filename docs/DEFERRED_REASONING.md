# Deferred Reasoning

`core/deferred_reasoning/` — SQLite-backed suspended reasoning recovery.

App handle: `app.deferred_reasoning`

Distinct from `cognitive_daemon` deferred store (P50).

## Enable

```env
ODIN_DEFERRED_REASONING_ENABLED=1
```

## API

- `POST /api/v1/runtime/deferred-reasoning/defer`
- `POST /api/v1/runtime/deferred-reasoning/restore`

## Channel

`deferred-reasoning:runtime`
