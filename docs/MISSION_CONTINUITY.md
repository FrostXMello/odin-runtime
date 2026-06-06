# Mission Continuity

`core/mission_continuity/` — long-horizon workflow continuity and recovery.

App handle: `app.mission_continuity`

## Enable

```env
ODIN_MISSION_CONTINUITY_ENABLED=1
ODIN_CONTINUITY_TRACKING_ENABLED=1
```

## API

- `GET /api/v1/runtime/mission-continuity/health`
- `POST /api/v1/runtime/mission-continuity/restore`
- `GET /api/v1/runtime/mission-continuity/resume-chain`

## Channel

`mission-continuity:runtime`

## Trace kinds

- `mission_resume_chain_built`
- `workflow_interruption_detected`

Integrates with `continuity_forecasting`, `workspace_sessions`, `overnight_cognition`, `operator_focus`.
