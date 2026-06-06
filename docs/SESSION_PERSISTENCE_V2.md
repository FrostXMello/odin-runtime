# Session Persistence V2

`core/session_persistence_v2/` — reliable cross-restart recovery and SQLite optimization.

App handle: `app.session_persistence_v2`

## Enable

```env
ODIN_SESSION_PERSISTENCE_V2_ENABLED=1
ODIN_SQLITE_COMPACTION_ENABLED=1
```

## API

- `POST /api/v1/runtime/session-persistence-v2/recover`
- `POST /api/v1/runtime/session-persistence-v2/compact`

## Channel

`session-persistence-v2:runtime`

## Trace kinds

- `session_registry_compacted`
- `runtime_recovery_completed`

Rolling checkpoint retention (200 max). Corruption-safe compaction with VACUUM scheduling.
