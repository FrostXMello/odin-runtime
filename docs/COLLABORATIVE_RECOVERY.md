# Collaborative Recovery

`core/collaborative_recovery/` — shared recovery authorization, collaborative rollback supervision, and multi-operator veto routing.

App handle: `app.collaborative_recovery`

## Enable

```env
ODIN_COLLABORATIVE_RECOVERY_ENABLED=1
ODIN_COLLABORATIVE_RECOVERY_MODE=supervised
```

## API

- `POST /api/v1/runtime/collaborative-recovery/request`
- `POST /api/v1/runtime/collaborative-recovery/authorize`
- `GET /api/v1/runtime/collaborative-recovery`

## Channel

`collaborative-recovery:runtime`

## Trace kinds

- `collaborative_recovery_requested`
- `shared_recovery_authorized`
- `collaborative_rollback_generated`
- `shared_continuity_restored`

Integrates with `operator_veto`, `rollback_intelligence`, and `continuity_recovery`. All shared recovery remains supervised and approval-gated.
