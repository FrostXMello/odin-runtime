# Engineering Evolution V2

`core/engineering_evolution_v2/` — supervised multi-repo engineering evolution.

App handle: `app.engineering_evolution_v2`

## Enable

```env
ODIN_ENGINEERING_EVOLUTION_V2_ENABLED=1
```

## API

- `POST /api/v1/runtime/multi-repo/reason`
- `POST /api/v1/runtime/regression-forecast/forecast`
- `POST /api/v1/runtime/engineering-evolution-v2/evaluate-patch`

## Channel

`engineering-evolution-v2:runtime`

Patches isolated in sandbox branches. Rollback plans mandatory. No protected-branch writes.
