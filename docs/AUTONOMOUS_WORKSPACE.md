# Autonomous Workspace

`core/autonomous_workspace/` — persistent session continuity and workflow recovery.

App handle: `app.autonomous_workspace`

Integrates: `project_memory`, `cognitive_kernel`, `workspace_presence`, `daily_continuity`, `conversation_workspace`

## Enable

```env
ODIN_AUTONOMOUS_WORKSPACE_ENABLED=1
ODIN_AUTONOMOUS_SESSION_RESTORE_ENABLED=1
```

## API

- `POST /api/v1/runtime/autonomous-workspace/open`
- `POST /api/v1/runtime/session-prediction/next`
- `POST /api/v1/runtime/workflow-recovery/recover`

## Channel

`workspace-autonomy:runtime`
