# Execution Confidence

`core/execution_confidence/` — execution certainty and workflow completion forecasting.

App handle: `app.execution_confidence`

## Enable

```env
ODIN_EXECUTION_CONFIDENCE_ENABLED=1
```

## API

- `GET /api/v1/runtime/execution-confidence`
- `POST /api/v1/runtime/execution-confidence/forecast`
- `GET /api/v1/runtime/workflow-forecast`

## Channel

`execution-confidence:runtime`

## Trace kinds

- `execution_confidence_estimated`
- `workflow_completion_forecasted`

Rollback confidence scoring. Supervised probability surfaces.
