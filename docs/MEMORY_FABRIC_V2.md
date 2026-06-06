# Memory Fabric V2

`core/memory_fabric_v2/` — persistent semantic memory and context resurrection.

App handle: `app.memory_fabric_v2`

## Enable

```env
ODIN_MEMORY_FABRIC_V2_ENABLED=1
ODIN_CONTEXT_REHYDRATION_ENABLED=1
```

## API

- `POST /api/v1/runtime/memory-fabric-v2/link`
- `POST /api/v1/runtime/context-rehydration/rehydrate`

## Channel

`memory-fabric-v2:runtime`

Integrates with `memory_fabric`, `project_memory`, `vector_memory`, and `cognitive_streams`.
