# Engineering Workflows V2

`core/engineering_workflows_v2/` — goal-to-execution planning with staged checkpoints.

App handle: `app.engineering_workflows_v2`

## Enable

```env
ODIN_ENGINEERING_WORKFLOWS_V2_ENABLED=1
```

## API

- `POST /api/v1/runtime/engineering-workflows/plan`
- `POST /api/v1/runtime/engineering-workflows/advance`
- `GET /api/v1/runtime/engineering-workflows/resume`

## Stages

`plan` → `implement` → `test` → `review` → `merge_proposal`

Trace: `implementation_stage_advanced`
