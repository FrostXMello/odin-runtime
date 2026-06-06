# Cognitive Maintenance

`core/cognitive_maintenance/` — memory consolidation and runtime stabilization.

App handle: `app.cognitive_maintenance`

## Enable

```env
ODIN_COGNITIVE_MAINTENANCE_ENABLED=1
```

## API

- `POST /api/v1/runtime/cognitive-maintenance/compact`
- `POST /api/v1/runtime/cognitive-maintenance/stabilize`

## Channel

`maintenance:runtime`

Integrates with `memory_fabric_v2`, `cognitive_streams`, `vector_memory`.
