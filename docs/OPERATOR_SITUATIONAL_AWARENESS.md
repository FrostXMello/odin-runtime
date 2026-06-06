# Operator Situational Awareness

`core/operator_situational_awareness/` — high-level cognitive awareness for the operator.

App handle: `app.operator_situational_awareness`

## Enable

```env
ODIN_OPERATOR_SITUATIONAL_AWARENESS_ENABLED=1
```

## API

- `GET /api/v1/runtime/operator-awareness`
- `GET /api/v1/runtime/operational-pressure`
- `GET /api/v1/runtime/operator-awareness/focus-risk`

## Channel

`operator-awareness:runtime`

## Trace kinds

- `operator_brief_generated`
- `operational_pressure_forecasted`

Integrates with `operator_focus`, `live_orchestration`. Local-only, transparent.
