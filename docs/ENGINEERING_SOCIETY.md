# Engineering Society

`core/engineering_society/` — supervised collaborative engineering teams.

App handle: `app.engineering_society`

## Roles

Architect · Backend Engineer · Frontend Engineer · Debugger · QA Engineer · DevOps Engineer · Reviewer · Research Engineer

## Enable

```env
ODIN_ENGINEERING_SOCIETY_ENABLED=1
```

## API

- `POST /api/v1/runtime/engineering-society/convene`

## Channel

`engineering-society:runtime`

Traces: `architecture_debate_started`, `review_consensus_reached`

All patch reviews remain supervised — no auto-merge to main.
