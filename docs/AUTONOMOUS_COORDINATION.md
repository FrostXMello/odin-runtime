# Autonomous Coordination

`core/autonomous_coordination/` — coordinated autonomous cognition orchestration.

App handle: `app.autonomous_coordination`

## Enable

```env
ODIN_AUTONOMOUS_COORDINATION_ENABLED=1
ODIN_COORDINATION_PROFILE=balanced
```

## API

- `GET /api/v1/runtime/autonomous-coordination`
- `POST /api/v1/runtime/autonomous-coordination/coordinate`
- `POST /api/v1/runtime/autonomous-coordination/recover`

## Channel

`autonomous-coordination:runtime`

## Trace kinds

- `runtime_coordination_started`
- `runtime_coordination_restored`

Integrates with `unified_cognitive_core`, `cognitive_scheduler`, `desktop_attention`, `autonomous_loop_v2`, `overnight_cognition`.

Operator-visible coordination. Approval-gated recovery. Coordination cooldowns.
