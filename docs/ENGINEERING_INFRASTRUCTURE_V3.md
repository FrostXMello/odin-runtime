# Engineering Infrastructure V3

`core/engineering_infrastructure_v3/` — supervised engineering operations infrastructure.

App handle: `app.engineering_infrastructure_v3`

## Enable

```env
ODIN_ENGINEERING_INFRASTRUCTURE_V3_ENABLED=1
ODIN_RELIABILITY_FORECASTING_ENABLED=1
```

## API

- `POST /api/v1/runtime/engineering-infrastructure/oversee`
- `POST /api/v1/runtime/reliability-forecast/forecast`

## Channel

`engineering-infrastructure:runtime`

**No auto-deploy. No protected branch writes. Rollback simulation required.**
