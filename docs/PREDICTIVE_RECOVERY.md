# Predictive Recovery

`core/predictive_recovery/` — blocker forecasting and recovery simulation.

App handle: `app.predictive_recovery`

## Enable

```env
ODIN_PREDICTIVE_RECOVERY_ENABLED=1
ODIN_RECOVERY_FORECASTING_ENABLED=1
```

## API

- `POST /api/v1/runtime/predictive-recovery/forecast`
- `POST /api/v1/runtime/predictive-recovery/simulate`
- `GET /api/v1/runtime/predictive-recovery/resilience`

## Channel

`predictive-recovery:runtime`

## Trace kinds

- `execution_failure_forecasted`
- `recovery_path_simulated`

Supervised forecasting. Approval-gated recovery paths. Predictive cooldowns.
