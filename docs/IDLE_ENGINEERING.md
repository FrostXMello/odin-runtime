# Idle Engineering

`core/idle_engineering/` — passive supervised repository analysis overnight.

App handle: `app.idle_engineering`

## Enable

```env
ODIN_IDLE_ENGINEERING_ENABLED=1
```

## API

- `GET /api/v1/runtime/idle-engineering/report`
- `POST /api/v1/runtime/idle-engineering/analyze`

## Channel

`idle-engineering:runtime`

**Strict rules:** NO automatic patch application. NO autonomous merge. NO deployment actions.

Integrates with `engineering_infrastructure_v3`, `validation_fabric`, `engineering_society`.
