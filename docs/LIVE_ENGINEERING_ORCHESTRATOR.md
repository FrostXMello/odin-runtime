# Live Engineering Orchestrator

`core/live_engineering_orchestrator/` — continuous engineering session orchestration.

App handle: `app.live_engineering_orchestrator`

## Enable

```env
ODIN_LIVE_ENGINEERING_ORCHESTRATOR_ENABLED=1
ODIN_LIVE_ENGINEERING_ENABLED=1
```

## API

- `POST /api/v1/runtime/live-engineering/observe`
- `POST /api/v1/runtime/live-engineering/restore`
- `POST /api/v1/runtime/live-engineering/profile`

## Profiles

`lightweight_engineering` · `balanced_engineering` · `autonomous_engineering` · `overnight_engineering`

## Traces

`engineering_goal_detected`, `engineering_session_restored` → `engineering-live:runtime`

Extends existing `live_engineering` runtime without rewriting it.
