# Workspace Sessions

`core/workspace_sessions/` — persistent workspace session registry.

App handle: `app.workspace_sessions`

## Enable

```env
ODIN_WORKSPACE_SESSIONS_ENABLED=1
```

## API

- `GET /api/v1/runtime/workspace-sessions`
- `POST /api/v1/runtime/workspace-sessions/save`
- `POST /api/v1/runtime/workspace-sessions/restore`
- `GET /api/v1/runtime/resume-chain`

## Channel

`workspace-sessions:runtime`

## Trace kinds

- `workspace_session_saved`
- `workspace_session_restored`

SQLite-backed persistence. Tracks repo state, active files, terminals, conversations, missions, overlays.

Supervised restore chains. No autonomous destructive execution.
