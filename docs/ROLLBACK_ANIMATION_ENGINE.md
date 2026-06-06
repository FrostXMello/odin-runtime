# Rollback Animation Engine

`core/rollback_animation_engine/` — live rollback DAG animation and execution chain playback.

App handle: `app.rollback_animation_engine`

## Enable

```env
ODIN_ROLLBACK_ANIMATION_ENGINE_ENABLED=1
ODIN_REPLAY_PROFILE=balanced
```

## API

- `GET /api/v1/runtime/rollback-animation/graph`
- `POST /api/v1/runtime/rollback-animation/replay`
- `POST /api/v1/runtime/rollback-animation/stabilize`
- `POST /api/v1/runtime/rollback-animation/synchronize`

## Channel

`rollback-animation:runtime`

## Trace kinds

- `rollback_animation_initialized`
- `rollback_dag_animated`
- `execution_chain_replayed`
- `rollback_render_stabilized`

Integrates with `rollback_intelligence`, `predictive_recovery_v2`, `live_cognition_timeline`, and `runtime_fusion`. DAG virtualization (800 node cap). Bounded replay loops (max 56). Approval-gated and supervised.
