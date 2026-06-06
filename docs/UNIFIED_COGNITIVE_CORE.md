# Unified Cognitive Core

`core/unified_cognitive_core/` — central orchestration layer above existing runtimes.

App handle: `app.unified_cognitive_core`

## Enable

```env
ODIN_UNIFIED_COGNITIVE_CORE_ENABLED=1
ODIN_GLOBAL_COGNITION_PROFILE=balanced
```

## API

- `GET /api/v1/runtime/unified-core/status`
- `POST /api/v1/runtime/unified-core/tick`
- `POST /api/v1/runtime/unified-core/synchronize`
- `POST /api/v1/runtime/unified-core/rebuild-context`

## Channel

`unified-core:runtime`

Does NOT directly execute patches or unrestricted actions. Orchestrates cognition, memory, attention, and scheduling.
