# Workspace Operations

`core/workspace_operations/` — live workspace operational state.

App handle: `app.workspace_operations`

## Enable

```env
ODIN_WORKSPACE_OPERATIONS_ENABLED=1
```

## API

- `GET /api/v1/runtime/workspace-operations/state`
- `POST /api/v1/runtime/workspace-operations/recover`

## Channel

`workspace-operations:runtime`

## Trace kinds

- `workspace_operation_recovered`

Tracks repos, terminals, branches, active files, missions. Integrates with `workspace_sessions`.
