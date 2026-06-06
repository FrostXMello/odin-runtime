# Self-Improvement Sandbox

`core/self_improvement_sandbox/` — isolated experimental upgrades.

App handle: `app.self_improvement_sandbox`

## Enable

```env
ODIN_SELF_IMPROVEMENT_SANDBOX_ENABLED=1
```

## API

- `POST /api/v1/runtime/self-improvement-sandbox/experiment`
- `POST /api/v1/runtime/self-improvement-sandbox/rollback-rehearsal`

## Channel

`sandbox:runtime`

## Constraints

No unrestricted modification. No production auto-deployments. All runs isolated to sandbox branches.
