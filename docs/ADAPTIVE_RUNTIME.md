# Adaptive Runtime

`core/adaptive_runtime/` — dynamic cognitive scaling and load balancing.

App handles: `app.adaptive_runtime`, `app.cognitive_load_balancer`

## Enable

```env
ODIN_ADAPTIVE_RUNTIME_ENABLED=1
ODIN_COGNITIVE_LOAD_BALANCING_ENABLED=1
```

## API

- `POST /api/v1/runtime/adaptive-runtime/scale`
- `POST /api/v1/runtime/cognition-load/balance`

## Channels

`adaptive-runtime:runtime`, `load-balancer:runtime`

## Profiles

`survival` · `balanced` · `immersive` · `cinematic` · `overnight_autonomous`
