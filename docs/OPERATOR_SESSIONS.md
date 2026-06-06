# Operator Sessions

`core/operator_sessions/` — operator identity, role, session continuity, and collaborative session replay.

App handle: `app.operator_sessions`

## Enable

```env
ODIN_OPERATOR_SESSIONS_ENABLED=1
```

## Tracked Fields

- operator role
- active missions
- approval authority
- focus state
- runtime ownership
- supervision scope

## API

- `POST /api/v1/runtime/operator-sessions/create`
- `GET /api/v1/runtime/operator-sessions/active`
- `GET /api/v1/runtime/operator-sessions/replay`

## Channel

`operator-sessions:runtime`

## Trace kinds

- `operator_session_created`
- `operator_session_restored`

SQLite-backed collaborative session registry (max 500 sessions). Lazy replay hydration.
