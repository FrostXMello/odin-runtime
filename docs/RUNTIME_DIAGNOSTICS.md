# Runtime Diagnostics

`core/runtime_diagnostics/` — runtime health inspection and integrity validation.

App handle: `app.runtime_diagnostics`

## Enable

```env
ODIN_RUNTIME_DIAGNOSTICS_ENABLED=1
```

## API

- `GET /api/v1/runtime/runtime-diagnostics/health`
- `POST /api/v1/runtime/runtime-diagnostics/report`
- `GET /api/v1/runtime/runtime-health`

## Channel

`runtime-diagnostics:runtime`

## Modes

`lightweight`, `deep`, `overnight`

## Trace kinds

- `runtime_health_inspected`
- `stream_anomaly_detected`
- `runtime_sync_validated`
- `checkpoint_integrity_verified`
