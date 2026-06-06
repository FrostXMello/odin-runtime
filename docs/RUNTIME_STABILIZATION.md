# Runtime Stabilization

`core/runtime_stabilization/` — instability suppression and fail-safe coordination.

App handle: `app.runtime_stabilization`

## Enable

```env
ODIN_RUNTIME_STABILIZATION_ENABLED=1
ODIN_RUNTIME_STABILIZATION_MODE=balanced
```

Modes: `lightweight`, `balanced`, `emergency`, `overnight`.

## API

- `POST /api/v1/runtime/runtime-stabilization/stabilize`
- `GET /api/v1/runtime/runtime-stabilization/health`

## Channel

`runtime-stabilization:runtime`

## Trace kinds

- `runtime_instability_detected` (shared with live orchestration)
- `runtime_stabilization_applied`

Runaway cognition prevention. Governance cooldowns. Degraded runtime recovery.
