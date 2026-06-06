# Reliability Forecasting

Reliability prediction via `ReliabilityPredictionRuntime` in engineering infrastructure V3.

## Enable

```env
ODIN_RELIABILITY_FORECASTING_ENABLED=1
ODIN_ENGINEERING_INFRASTRUCTURE_V3_ENABLED=1
```

## API

- `POST /api/v1/runtime/reliability-forecast/forecast`

Trace: `reliability_risk_detected` → `engineering-infrastructure:runtime`

Operator page: `/reliability-forecast`

Approval checkpoints mandatory for high-risk changes.
