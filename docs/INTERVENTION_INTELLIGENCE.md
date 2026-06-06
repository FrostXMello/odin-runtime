# Intervention Intelligence

`core/intervention_intelligence/` — operator intervention forecasting.

App handle: `app.intervention_intelligence`

## Enable

```env
ODIN_INTERVENTION_INTELLIGENCE_ENABLED=1
```

## API

- `GET /api/v1/runtime/intervention-intelligence`
- `POST /api/v1/runtime/intervention-intelligence/forecast`
- `GET /api/v1/runtime/operator-overload`

## Channel

`intervention-intelligence:runtime`

## Trace kinds

- `operator_intervention_forecasted`
- `operator_overload_detected`

Transparent forecasting. Operator override required. Integrates with `operator_situational_awareness`.
