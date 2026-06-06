# Cognitive Risk

`core/cognitive_risk/` — execution risk estimation and failure simulation.

App handle: `app.cognitive_risk`

## Enable

```env
ODIN_COGNITIVE_RISK_ENABLED=1
ODIN_RISK_FORECASTING_MODE=adaptive
```

Risk categories: execution, continuity, cognition, coordination, overload, intervention.

## API

- `POST /api/v1/runtime/cognitive-risk/forecast`
- `POST /api/v1/runtime/cognitive-risk/simulate`

## Channel

`cognitive-risk:runtime`

## Trace kinds

- `cognitive_risk_forecasted`
- `failure_chain_simulated`
- `governance_drift_detected`

Bounded simulation loops (max 36). Supervised forecasting.
