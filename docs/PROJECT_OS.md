# Project OS (v0.36)

Persistent project operating memory for coding continuity.

## Orchestrator

`app.project_os` — `ProjectOSRuntime`

## Configuration

```env
ODIN_PROJECT_OS_ENABLED=true
```

## APIs

- `GET /api/v1/runtime/projects`
- `POST /api/v1/runtime/projects/register`
- `POST /api/v1/runtime/projects/{id}/restore`
