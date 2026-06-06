# Production Observability

`core/production_observability/` — production telemetry and operational profiling.

App handle: `app.production_observability`

## Enable

```env
ODIN_PRODUCTION_OBSERVABILITY_ENABLED=1
ODIN_STARTUP_OPTIMIZATION_ENABLED=1
```

## API

- `GET /api/v1/runtime/production-observability/metrics`
- `GET /api/v1/runtime/production-observability/profile`
- `GET /api/v1/runtime/startup-profiler`
- `GET /api/v1/runtime/runtime-metrics`

## Channel

`production-observability:runtime`

## Trace kinds

- `runtime_metrics_generated`
- `operational_profile_generated`
- `startup_performance_measured`

Local-first metrics export. No cloud dependencies.
