# Objective Management

`core/objective_management/` — persistent objective trees and progress tracking.

App handle: `app.objective_management`

## Enable

```env
ODIN_OBJECTIVE_MANAGEMENT_ENABLED=1
```

## API

- `GET /api/v1/runtime/objectives/active`
- `POST /api/v1/runtime/objectives/create`
- `POST /api/v1/runtime/objectives/progress`
- `GET /api/v1/runtime/objectives/stalled`

## Channel

`objective-management:runtime`

## Trace kinds

- `objective_tree_created`
- `objective_progress_updated`
- `stalled_objective_detected`

SQLite-backed registry with bounded retention (200 objectives). Approval checkpoints required.
