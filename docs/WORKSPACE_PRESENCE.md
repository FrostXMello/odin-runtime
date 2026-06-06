# Workspace Presence

`core/workspace_presence/` — deep engineering workspace integration.

## Correlates

- Repositories and branches
- Terminal state
- Editor tabs
- Browser docs
- Runtime logs (via context fusion)

## API

- `POST /api/v1/runtime/workspace-presence/observe`
- `POST /api/v1/runtime/workspace-presence/restore`

Channel: `workspace:presence`

Trace: `workspace_context_restored`
