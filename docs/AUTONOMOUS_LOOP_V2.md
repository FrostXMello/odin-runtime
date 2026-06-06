# Autonomous Loop V2

`core/autonomous_loop_v2/` — persistent bounded autonomous agent loop.

App handle: `app.autonomous_loop_v2`

## Enable

```env
ODIN_AUTONOMOUS_LOOP_V2_ENABLED=1
ODIN_AUTONOMOUS_OVERNIGHT_MODE_ENABLED=1
```

## API

- `POST /api/v1/runtime/autonomous-loop-v2/resume-goal`
- `POST /api/v1/runtime/long-horizon-planning/plan`
- `POST /api/v1/runtime/autonomous-loop-v2/tick`

## Channel

`autonomous-loop-v2:runtime`

**Strict limits:** approval required for execution, no self-modifying source writes, recursion depth bounded.
