# Continuity Forecasting

`core/continuity_forecasting/` — predict tomorrow's work and abandoned workflows.

App handle: `app.continuity_forecasting`

## Enable

```env
ODIN_CONTINUITY_FORECASTING_ENABLED=1
```

## API

- `GET /api/v1/runtime/continuity-forecast`

## Channel

`continuity-forecast:runtime`

Integrates with `project_memory`, `workspace_coordination`, `operator_intelligence_v4`, `memory_intelligence`.
