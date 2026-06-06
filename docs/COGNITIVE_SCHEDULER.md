# Cognitive Scheduler

`core/cognitive_scheduler/` — bounded scheduling and deferred queues.

App handle: `app.cognitive_scheduler`

## Enable

```env
ODIN_COGNITIVE_SCHEDULER_ENABLED=1
```

## API

- `POST /api/v1/runtime/cognitive-scheduler/schedule`
- `POST /api/v1/runtime/cognitive-scheduler/defer`
- `POST /api/v1/runtime/cognitive-scheduler/restore`

## Channel

`scheduler:runtime`

Integrates with `cognitive_daemon_v2`, `adaptive_runtime`, `autonomous_loop_v2`.
