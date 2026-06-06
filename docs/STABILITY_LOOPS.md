# Stability Loops

`core/stability_loops/` — bounded stabilization loops and recovery throttling.

App handle: `app.stability_loops`

## Enable

```env
ODIN_STABILITY_LOOPS_ENABLED=1
ODIN_STABILITY_MODE=balanced
```

## API

- `POST /api/v1/runtime/stability-loops/rebalance`
- `POST /api/v1/runtime/stability-loops/throttle`
- `GET /api/v1/runtime/stability-loops`
- `GET /api/v1/runtime/runtime-stability`

## Channel

`stability-loops:runtime`

## Trace kinds

- `stability_loop_initialized`
- `instability_cascade_suppressed`
- `recovery_density_throttled`

Integrates with `runtime_stabilization`, `unified_command_center`, `runtime_fusion`.

Bounded stabilization loops (max 48). Low-power recovery scheduling.
