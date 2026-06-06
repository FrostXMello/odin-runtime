# Predictive Governance

`core/predictive_governance/` — governance orchestration and pressure balancing.

App handle: `app.predictive_governance`

## Enable

```env
ODIN_PREDICTIVE_GOVERNANCE_ENABLED=1
ODIN_GOVERNANCE_PROFILE=balanced
```

## API

- `GET /api/v1/runtime/predictive-governance/status`
- `POST /api/v1/runtime/predictive-governance/rebalance`
- `GET /api/v1/runtime/governance-health`

## Channel

`predictive-governance:runtime`

## Trace kinds

- `governance_cycle_initialized`
- `governance_pressure_rebalanced`

Integrates with `unified_cognitive_core`, `distributed_execution`, `autonomous_coordination`, `execution_system`, `cognitive_scheduler`, `autonomous_workflows`.

Operator-supervised. Reversible checkpoints. Bounded governance.
