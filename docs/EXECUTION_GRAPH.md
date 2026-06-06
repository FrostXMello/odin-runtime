# Execution Graph

`core/execution_graph/` — execution DAG management.

App handle: `app.execution_graph`

## Enable

```env
ODIN_EXECUTION_GRAPH_ENABLED=1
ODIN_EXECUTION_DAG_MODE=adaptive
```

## API

- `POST /api/v1/runtime/execution-graph/build`
- `GET /api/v1/runtime/execution-graph/topology`
- `GET /api/v1/runtime/rollback-graph`

## Channel

`execution-graph:runtime`

## Trace kinds

- `execution_dag_generated`
- `rollback_graph_generated`

SQLite DAG registry (max 400 nodes). Adaptive virtualization. Reversible rollback graphs.
