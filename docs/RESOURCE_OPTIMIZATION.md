# Resource Optimization

`core/resource_optimization/` — adaptive memory reduction and low-power coordination (extended v0.64).

App handle: `app.resource_optimization`

## Enable

```env
ODIN_RESOURCE_OPTIMIZATION_ENABLED=1
ODIN_RESOURCE_PROFILE=balanced
ODIN_LOW_POWER_COORDINATION=1
```

## API

- `POST /api/v1/runtime/resource-optimization/rebalance`
- `POST /api/v1/runtime/resource-optimization/low-power`
- `POST /api/v1/runtime/resource-optimization/compress`
- `POST /api/v1/runtime/resource-optimization/memory`

## Channel

`resource-optimization:runtime`

## Trace kinds

- `runtime_surfaces_compressed`
- `memory_pressure_optimized`

Target hardware: GTX 1650 Ti, 16GB RAM, M-series MacBook.
