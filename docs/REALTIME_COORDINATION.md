# Realtime Coordination

`core/realtime_coordination/` — live runtime balancing and stream multiplexing.

App handle: `app.realtime_coordination`

## Enable

```env
ODIN_REALTIME_COORDINATION_ENABLED=1
```

## API

- `GET /api/v1/runtime/realtime-coordination`
- `POST /api/v1/runtime/realtime-coordination/multiplex`
- `POST /api/v1/runtime/realtime-coordination/stabilize`

## Channel

`realtime-coordination:runtime`

## Trace kinds

- `runtime_stream_multiplexed`
- `coordination_pressure_updated`

Bounded multiplexing (max 48). Coordination stabilization with cooldowns.
