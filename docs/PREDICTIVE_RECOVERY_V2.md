# Predictive Recovery V2

`core/predictive_recovery_v2/` — predictive instability detection and recovery path simulation.

App handle: `app.predictive_recovery_v2`

Distinct from P58 `predictive_recovery`. V2 adds operational failure forecasting, recovery probability estimation, and operator veto routing.

## Enable

```env
ODIN_PREDICTIVE_RECOVERY_V2_ENABLED=1
ODIN_RECOVERY_PROFILE=balanced
```

## API

- `POST /api/v1/runtime/predictive-recovery-v2/forecast`
- `POST /api/v1/runtime/predictive-recovery-v2/simulate`
- `GET /api/v1/runtime/predictive-recovery-v2`

## Channel

`predictive-recovery-v2:runtime`

## Trace kinds

- `operational_failure_forecasted`
- `recovery_paths_simulated`
- `recovery_probability_estimated`

Integrates with `predictive_governance`, `runtime_stabilization`, `distributed_execution`, `execution_system`, `mission_command`, `cognitive_risk`, `operator_veto`.

Approval-gated recommendations. Bounded simulation loops (max 36).
