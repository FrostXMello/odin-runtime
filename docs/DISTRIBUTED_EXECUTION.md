# Distributed Execution

`core/distributed_execution/` — cross-workspace execution federation.

App handle: `app.distributed_execution`

## Enable

```env
ODIN_DISTRIBUTED_EXECUTION_ENABLED=1
ODIN_DISTRIBUTED_PROFILE=balanced
```

## API

- `POST /api/v1/runtime/distributed-execution/federate`
- `GET /api/v1/runtime/distributed-execution/health`
- `POST /api/v1/runtime/distributed-execution/synchronize`

## Channel

`distributed-execution:runtime`

## Trace kinds

- `distributed_execution_federated`
- `distributed_pipeline_synchronized`

Approval-gated. Reversible recovery. Integrates with `cross_workspace_coordination`, `execution_system`.
