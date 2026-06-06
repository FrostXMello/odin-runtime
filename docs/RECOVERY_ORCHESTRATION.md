# Recovery Orchestration

`core/recovery_orchestration/` — supervised recovery coordination and phase transitions.

App handle: `app.recovery_orchestration`

## Phases

`detection`, `stabilization`, `rollback_review`, `recovery_execution`, `validation`, `continuity_restore`

## Enable

```env
ODIN_RECOVERY_ORCHESTRATION_ENABLED=1
```

## API

- `POST /api/v1/runtime/recovery-orchestration/initialize`
- `POST /api/v1/runtime/recovery-orchestration/transition`
- `GET /api/v1/runtime/recovery-orchestration`
- `GET /api/v1/runtime/recovery-phases`

## Channel

`recovery-orchestration:runtime`

## Trace kinds

- `recovery_cycle_initialized`
- `recovery_phase_transitioned`

All recovery execution routes through `operator_veto` for authorization. Bounded recovery cycles (max 48).
