# Operator Focus

`core/operator_focus/` — focus session coordination and distraction estimation.

App handle: `app.operator_focus`

## Enable

```env
ODIN_OPERATOR_FOCUS_ENABLED=1
```

## API

- `GET /api/v1/runtime/operator-focus/state`
- `POST /api/v1/runtime/operator-focus/start`
- `GET /api/v1/runtime/operator-focus/pressure`
- `GET /api/v1/runtime/focus-recovery`

## Channel

`operator-focus:runtime`

## Trace kinds

- `focus_session_started`
- `focus_breakdown_detected`

Integrates with `operator_intelligence_v3`, `attention_engine`, `continuity_forecasting`.

Operator-controlled sessions. Transparent distraction pressure. Recovery recommendations require operator override.
