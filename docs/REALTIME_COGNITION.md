# Realtime Cognition

`core/realtime_cognition/` — persistent real-time cognitive infrastructure.

App handles: `app.realtime_cognition`, `app.attention_flow`

## Enable

```env
ODIN_REALTIME_COGNITION_ENABLED=1
ODIN_CONTINUOUS_REASONING_ENABLED=1
```

## API

- `POST /api/v1/runtime/realtime-cognition/heartbeat`
- `POST /api/v1/runtime/realtime-cognition/reason`
- `POST /api/v1/runtime/attention-flow/route`

## Channels

`realtime-cognition:runtime`, `desktop-v3:runtime`

Integrates with `cognitive_kernel`, `adaptive_runtime`, `cognitive_streams`, `cognitive_daemon_v2`.
