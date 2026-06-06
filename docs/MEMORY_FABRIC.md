# Memory Fabric

`core/memory_fabric/` — unified persistent memory graph.

App handle: `app.memory_fabric`

Integrates: `memory_threads`, `project_memory`, vector memory, engineering memory, conversational memory.

## Enable

```env
ODIN_MEMORY_FABRIC_ENABLED=1
```

## API

- `POST /api/v1/runtime/memory-fabric/link`
- `POST /api/v1/runtime/memory-fabric/recall`

## Channel

`memory-fabric:runtime`

Trace: `memory_fabric_linked`
