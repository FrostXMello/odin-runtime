# Mission Graph

`core/mission_graph/` — persistent mission dependency graph.

App handle: `app.mission_graph`

## Enable

```env
ODIN_MISSION_GRAPH_ENABLED=1
```

## API

- `GET /api/v1/runtime/mission-graph`
- `POST /api/v1/runtime/mission-graph/link`
- `GET /api/v1/runtime/mission-graph/continuity`

## Channel

`mission-graph:runtime`

## Trace kinds

- `mission_graph_linked`

SQLite-backed graph registry (max 300 nodes). Graph virtualization for large graphs.

Integrates with `mission_continuity`, `objective_management`.
