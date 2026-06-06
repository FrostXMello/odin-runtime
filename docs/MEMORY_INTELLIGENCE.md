# Memory Intelligence

`core/memory_intelligence/` — advanced semantic memory intelligence.

App handle: `app.memory_intelligence`

## Enable

```env
ODIN_MEMORY_INTELLIGENCE_ENABLED=1
```

## API

- `POST /api/v1/runtime/memory-intelligence/relate`
- `POST /api/v1/runtime/predictive-memory/resurface`

## Channel

`memory-intelligence:runtime`

Integrates with `memory_fabric_v2`, `vector_memory`, `project_memory`, `cognitive_streams`.
