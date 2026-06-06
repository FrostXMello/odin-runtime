# Cognitive Orchestration

`core/cognitive_orchestration/` — synchronized cognition daemon layer.

App handle: `app.cognitive_orchestration`

Extends `cognitive_daemon` without replacing it.

## Enable

```env
ODIN_COGNITIVE_ORCHESTRATION_ENABLED=1
ODIN_COGNITIVE_DAEMON_ENABLED=1
```

## API

- `POST /api/v1/runtime/cognitive-orchestration/tick`
- `POST /api/v1/runtime/cognitive-orchestration/overnight`
- `POST /api/v1/runtime/cognitive-orchestration/defer`

## Channel

`cognitive-orchestration:runtime`

Traces: `cognitive_tick_executed`, `overnight_reflection_completed`, `cross_runtime_sync_completed`

Resource profiles dynamically pause heavy cognition under pressure.
