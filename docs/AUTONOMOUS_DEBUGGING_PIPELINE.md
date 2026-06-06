# Autonomous Debugging Pipeline

Extends `core/autonomous_debugging/` with supervised pipeline modules.

App handle: `app.autonomous_debugging_pipeline`

## Modules

`trace_analyzer`, `failure_clusterer`, `stack_reasoner`, `patch_hypothesis`, `regression_predictor`, `confidence_gates`

## Enable

```env
ODIN_AUTONOMOUS_DEBUGGING_ENABLED=1
```

## API

- `POST /api/v1/runtime/autonomous-debugging/analyze`
- `POST /api/v1/runtime/autonomous-debugging/map-tests`

## Channel

`debugging-live:runtime`

## Constraints

**No direct automatic patching.** Hypotheses are confidence-gated and approval-required.
