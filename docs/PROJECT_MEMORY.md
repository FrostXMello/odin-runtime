# Project Memory

`core/project_memory/` — persistent repository cognition.

App handle: `app.project_memory`

## Enable

```env
ODIN_PROJECT_MEMORY_ENABLED=1
```

## API

- `POST /api/v1/runtime/project-memory/remember`
- `POST /api/v1/runtime/project-memory/resume`

## Channel

`project-memory:runtime`

Features: timeline replay, decision memory, architecture memory, issue recurrence, instant resume.
