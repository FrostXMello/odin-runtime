# Autonomous Workflows

`core/autonomous_workflows/` — bounded supervised automation loops.

App handle: `app.autonomous_workflows`

## Enable

```env
ODIN_AUTONOMOUS_WORKFLOWS_ENABLED=1
```

## API

- `POST /api/v1/runtime/autonomous-workflows/continue`
- `POST /api/v1/runtime/autonomous-workflows/checkpoint`
- `GET /api/v1/runtime/autonomous-workflows`

## Channel

`autonomous-workflows:runtime`

## Trace kinds

- `autonomous_workflow_continued`
- `workflow_state_checkpointed`

Bounded cycles (max 48). No auto-deploy. Reversible checkpoints (max 24). Low-power workflow compression.
