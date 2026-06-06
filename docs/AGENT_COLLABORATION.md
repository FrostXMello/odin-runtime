# Agent Collaboration

`core/agent_collaboration/` — structured multi-agent workflows.

App handle: `app.agent_collaboration`

## Enable

```env
ODIN_AGENT_COLLABORATION_ENABLED=1
```

Agents: Architect, Debugger, Researcher, Planner, Reviewer, Refactor, DevOps, Documentation.

## API

- `POST /api/v1/runtime/agent-collaboration/initiate`
- `GET /api/v1/runtime/agent-collaboration/consensus`

## Channel

`agent-collaboration:runtime`

## Trace kinds

- `agent_collaboration_started`
- `consensus_score_updated`

Operator-visible reasoning. Approval-gated routing. Local-only.
