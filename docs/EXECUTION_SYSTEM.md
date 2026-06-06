# Execution System

`core/execution_system/` — supervised execution coordination.

App handle: `app.execution_system`

## Enable

```env
ODIN_EXECUTION_SYSTEM_ENABLED=1
ODIN_EXECUTION_PROFILE=balanced
```

## API

- `POST /api/v1/runtime/execution-system/start`
- `POST /api/v1/runtime/execution-system/checkpoint`
- `POST /api/v1/runtime/execution-system/rollback`
- `GET /api/v1/runtime/execution-system/health`

## Channel

`execution-system:runtime`

## Trace kinds

- `execution_pipeline_initialized`
- `execution_stage_checkpointed`
- `execution_stage_rolled_back`
- `execution_health_updated`

Approval-gated. Reversible. Bounded checkpoints (max 32).
