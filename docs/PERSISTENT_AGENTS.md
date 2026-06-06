# Persistent Agents

`core/persistent_agents/` — SQLite-backed supervised persistent agents.

App handle: `app.persistent_agents`

## Enable

```env
ODIN_PERSISTENT_AGENTS_ENABLED=1
```

## Default Agents

Architect, Debugger, Researcher, Reviewer, Optimizer, Planner, Documentation, Infrastructure

## API

- `GET /api/v1/runtime/persistent-agents`
- `POST /api/v1/runtime/persistent-agents/assign`

## Channel

`persistent-agents:runtime`

NO unrestricted autonomy. Agents remain supervised with approval-gated objectives.
