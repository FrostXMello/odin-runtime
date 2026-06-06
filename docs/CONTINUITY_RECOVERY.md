# Continuity Recovery

`core/continuity_recovery/` — mission continuity preservation and cognition restoration.

App handle: `app.continuity_recovery`

## Enable

```env
ODIN_CONTINUITY_RECOVERY_ENABLED=1
```

## API

- `POST /api/v1/runtime/continuity-recovery/restore`
- `GET /api/v1/runtime/continuity-recovery/window`
- `GET /api/v1/runtime/continuity-recovery`

## Channel

`continuity-recovery:runtime`

## Trace kinds

- `mission_continuity_restored`
- `workspace_context_rebuilt`

Integrates with `mission_command`, `mission_continuity`, `context_synchronization`, `deferred_reasoning`, `live_cognition_timeline`.

Reversible restoration. Lazy continuity hydration. Bounded replay (max 40).
