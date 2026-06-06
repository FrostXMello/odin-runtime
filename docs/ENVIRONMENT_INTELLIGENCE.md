# Environment Intelligence

`core/environment_intelligence/` — live workspace understanding.

App handle: `app.environment_intelligence`

## Enable

```env
ODIN_ENVIRONMENT_INTELLIGENCE_ENABLED=1
```

## API

- `POST /api/v1/runtime/environment-intelligence/observe`

## Channel

`environment:runtime`

Traces: `environment_context_detected`, `workflow_prediction_generated`
