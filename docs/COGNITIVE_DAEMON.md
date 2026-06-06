# Cognitive Daemon

`core/cognitive_daemon/` — continuous cognitive presence orchestration.

Extends existing `daemon_runtime` without rewriting it.

## Modules

- `daemon_orchestrator.py` — `CognitiveDaemonOrchestrator` (`app.cognitive_daemon`)
- `continuous_attention.py` — heartbeat
- `idle_reasoning.py` — deferred thoughts
- `proactive_memory_refresh.py` — memory refresh
- `background_reflection.py` — overnight-style reflection
- `environment_awareness_loop.py` — live environment sync
- `task_resumption.py` — unfinished work resurfacing
- `adaptive_focus_scheduler.py` — resource-aware tick intervals

## Enable

```env
ODIN_COGNITIVE_DAEMON_ENABLED=1
```

## API

- `POST /api/v1/runtime/cognitive-daemon/tick`
- `POST /api/v1/runtime/cognitive-daemon/profile`

## Channel

`daemon-cognition:runtime`

## Traces

`daemon_attention_shifted`, `unfinished_task_resurfaced`

Resource-aware for GTX 1650 Ti, 16GB RAM, M-series MacBooks.
