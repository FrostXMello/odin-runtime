# Runtime Cleanup

`core/runtime_cleanup/` — stale runtime, orphan stream, and replay cache cleanup.

App handle: `app.runtime_cleanup`

## Enable

```env
ODIN_RUNTIME_CLEANUP_ENABLED=1
```

## API

- `POST /api/v1/runtime/runtime-cleanup/run`
- `GET /api/v1/runtime/runtime-cleanup/status`

## Channel

`runtime-cleanup:runtime`

## Modes

`passive`, `aggressive`, `overnight`

## Trace kinds

- `orphan_runtime_state_cleaned`
- `replay_windows_cleaned`

Background cleanup scheduling with operator-visible activity.
