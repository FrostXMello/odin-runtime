# Task Orchestration

`core/task_orchestration/` — multi-stage execution pipelines.

App handle: `app.task_orchestration`

## Enable

```env
ODIN_TASK_ORCHESTRATION_ENABLED=1
ODIN_EXECUTION_QUEUE_MODE=adaptive
```

## API

- `GET /api/v1/runtime/task-orchestration/queue`
- `POST /api/v1/runtime/task-orchestration/pipeline`
- `POST /api/v1/runtime/task-orchestration/rebalance`

## Channel

`task-orchestration:runtime`

## Trace kinds

- `execution_queue_rebalanced`
- `execution_blocker_detected`

Bounded queue (max 64). Blocker detection with operator visibility.
