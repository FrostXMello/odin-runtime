# Continuous Engineering

`core/continuous_engineering/` — resource-aware engineering daemon.

App handle: `app.continuous_engineering`

Extends `cognitive_daemon` without rewriting it.

## Enable

```env
ODIN_CONTINUOUS_ENGINEERING_ENABLED=1
ODIN_COGNITIVE_DAEMON_ENABLED=1
```

## API

- `POST /api/v1/runtime/continuous-engineering/tick`
- `POST /api/v1/runtime/continuous-engineering/overnight`

## Channels

`repo-watch:runtime`, `daemon-cognition:runtime`

Trace: `overnight_analysis_completed`

Resource-aware for GTX 1650 Ti, 16GB RAM, M-series MacBooks.
