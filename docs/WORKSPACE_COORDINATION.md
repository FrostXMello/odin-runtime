# Workspace Coordination

`core/workspace_coordination/` — multi-workspace cognitive coordination.

App handle: `app.workspace_coordination`

## Enable

```env
ODIN_WORKSPACE_COORDINATION_ENABLED=1
```

## API

- `POST /api/v1/runtime/workspace-coordination/coordinate`
- `POST /api/v1/runtime/multi-project-timeline/unify`

## Channel

`workspace-coordination:runtime`

Integrates with `workspace_presence`, `autonomous_workspace`, `memory_fabric_v2`, `engineering_evolution_v2`.
