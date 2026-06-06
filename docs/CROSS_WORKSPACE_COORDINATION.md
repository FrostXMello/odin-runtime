# Cross Workspace Coordination

`core/cross_workspace_coordination/` — multi-project workspace federation.

App handle: `app.cross_workspace_coordination`

Distinct from P51 `workspace_coordination`.

## Enable

```env
ODIN_CROSS_WORKSPACE_COORDINATION_ENABLED=1
```

## API

- `GET /api/v1/runtime/cross-workspace/map`
- `POST /api/v1/runtime/cross-workspace/synchronize`

## Channel

`cross-workspace:runtime`

## Trace kinds

- `workspace_contexts_synchronized`
- `workspace_dependency_pressure_updated`

Bounded federation loops (max 40). Local-first. Integrates with `context_synchronization`, `workspace_operations`.
