# Predictive Operator Intelligence

`core/operator_intelligence_v4/` — predictive operator assistance V4.

App handle: `app.operator_intelligence_v4`

## Enable

```env
ODIN_OPERATOR_INTELLIGENCE_V4_ENABLED=1
ODIN_PREDICTIVE_FOCUS_ENABLED=1
```

## API

- `POST /api/v1/runtime/operator-intelligence-v4/predict`
- `POST /api/v1/runtime/predictive-focus/forecast`
- `POST /api/v1/runtime/cognitive-load-forecast/forecast`

## Channel

`operator-intelligence-v4:runtime`

Local-only telemetry. Transparent predictions. Operator override always available.
