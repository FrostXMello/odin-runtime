# Overnight Cognition

`core/overnight_cognition/` — persistent overnight cognitive orchestration.

App handle: `app.overnight_cognition`

## Enable

```env
ODIN_OVERNIGHT_COGNITION_ENABLED=1
ODIN_OVERNIGHT_MODE=balanced
ODIN_OVERNIGHT_MAX_CYCLES=32
```

## API

- `POST /api/v1/runtime/overnight/start`
- `POST /api/v1/runtime/overnight/pause`
- `GET /api/v1/runtime/overnight/summary`

## Channel

`overnight:runtime`

Integrates with `unified_cognitive_core`, `cognitive_scheduler`, `cognitive_daemon_v2`, `autonomous_loop_v2`.

No autonomous deployment. Bounded cognition cycles only.
