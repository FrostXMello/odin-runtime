# Replay Orchestration

`core/replay_orchestration/` — replay coordination and bounded cognition playback.

App handle: `app.replay_orchestration`

## Enable

```env
ODIN_REPLAY_ORCHESTRATION_ENABLED=1
ODIN_REPLAY_DENSITY=adaptive
```

## API

- `POST /api/v1/runtime/replay-orchestration/window`
- `POST /api/v1/runtime/replay-orchestration/throttle`
- `POST /api/v1/runtime/replay-orchestration/replay`
- `POST /api/v1/runtime/replay-orchestration/checkpoint`

## Channel

`replay-orchestration:runtime`

## Trace kinds

- `replay_window_initialized`
- `cognition_timeline_replayed`
- `replay_state_checkpointed`
- `replay_density_throttled`

Integrates with `live_cognition_timeline`, `continuity_recovery`, `mission_continuity`, and `operator_veto`. Approval-gated replay windows. Bounded replay loops (max 56).
