# Engineering Evolution

`core/autonomous_engineering_evolution/` — supervised repository evolution analysis.

App handle: `app.engineering_evolution`

## Enable

```env
ODIN_ENGINEERING_EVOLUTION_ENABLED=1
```

## API

- `POST /api/v1/runtime/engineering-evolution/analyze`
- `POST /api/v1/runtime/upgrade-planning/propose`

## Channel

`engineering-evolution:runtime`

**No auto-merge. No auto-deploy. Rollback plan mandatory.**
