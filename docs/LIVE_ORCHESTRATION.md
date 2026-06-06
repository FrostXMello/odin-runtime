# Live Orchestration

`core/live_orchestration/` — real-time orchestration visibility and cognition pulse.

App handle: `app.live_orchestration`

## Enable

```env
ODIN_LIVE_ORCHESTRATION_ENABLED=1
ODIN_ORCHESTRATION_PROFILE=balanced
```

## API

- `GET /api/v1/runtime/live-orchestration`
- `POST /api/v1/runtime/live-orchestration/stream`
- `GET /api/v1/runtime/live-orchestration/health`
- `POST /api/v1/runtime/live-orchestration/pulse`

## Channel

`live-orchestration:runtime`

## Trace kinds

- `orchestration_state_streamed`
- `runtime_instability_detected`

Integrates with `autonomous_coordination`, `context_synchronization`, `desktop_attention`.

Orchestration throttling, runtime cooldowns, low-power cinematic mode.
