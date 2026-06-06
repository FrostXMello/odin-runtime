# Context Synchronization

`core/context_synchronization/` — cross-runtime context alignment.

App handle: `app.context_synchronization`

## Enable

```env
ODIN_CONTEXT_SYNCHRONIZATION_ENABLED=1
```

## API

- `GET /api/v1/runtime/context-sync/state`
- `POST /api/v1/runtime/context-sync/synchronize`
- `POST /api/v1/runtime/context-sync/merge`
- `GET /api/v1/runtime/context-sync/divergence`

## Channel

`context-sync:runtime`

## Trace kinds

- `context_surfaces_synchronized`
- `context_divergence_detected`

Integrates with `memory_fabric_v2`, `workspace_sessions`, `project_memory`. Bounded sync loops (max 32).
