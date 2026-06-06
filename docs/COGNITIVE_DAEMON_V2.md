# Cognitive Daemon V2

Extends `core/cognitive_daemon/` with overnight cycles, deferred reasoning, and low-power mode.

App handle: `app.cognitive_daemon_v2`

## Enable

```env
ODIN_COGNITIVE_DAEMON_V2_ENABLED=1
ODIN_OVERNIGHT_COGNITION_ENABLED=1
ODIN_COGNITIVE_DAEMON_ENABLED=1
```

## API

- `POST /api/v1/runtime/cognitive-orchestration/daemon-v2/overnight`
- `POST /api/v1/runtime/cognitive-orchestration/daemon-v2/defer`
- `POST /api/v1/runtime/cognitive-orchestration/daemon-v2/resume`

## Channel

`daemon-v2:runtime`
