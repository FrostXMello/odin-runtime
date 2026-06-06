# Team Coordination

`core/team_coordination/` — team synchronization, workload pressure, interruption routing, and collaborative focus stabilization.

App handle: `app.team_coordination`

## Enable

```env
ODIN_TEAM_COORDINATION_ENABLED=1
ODIN_TEAM_SYNC_MODE=adaptive
```

## API

- `GET /api/v1/runtime/team-coordination/pressure`
- `POST /api/v1/runtime/team-coordination/rebalance`
- `GET /api/v1/runtime/team-coordination`

## Channel

`team-coordination:runtime`

## Trace kinds

- `team_attention_rebalanced`
- `team_pressure_updated`
- `cross_operator_noise_suppressed`

Bounded attention rebalance loops (max 48). Low-power supervisory mode via cross-operator noise suppression.
