# Pressure Propagation

`core/pressure_propagation/` — runtime pressure diffusion and congestion detection.

App handle: `app.pressure_propagation`

## Enable

```env
ODIN_PRESSURE_PROPAGATION_ENABLED=1
```

## API

- `GET /api/v1/runtime/pressure-propagation/state`
- `POST /api/v1/runtime/pressure-propagation/rebalance`
- `GET /api/v1/runtime/pressure-diffusion`
- `POST /api/v1/runtime/pressure-propagation/congestion`

## Channel

`pressure-propagation:runtime`

## Trace kinds

- `runtime_pressure_propagated`
- `pressure_diffusion_simulated`
- `execution_congestion_detected`
- `pressure_surfaces_rebalanced`

Integrates with `runtime_fusion` and `stability_loops`. Operator-visible pressure surfaces with reversible rebalancing.
