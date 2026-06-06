# Context Rehydration

Restores replayable engineering session context via `ContextRehydrationEngine`.

## Enable

```env
ODIN_CONTEXT_REHYDRATION_ENABLED=1
ODIN_MEMORY_FABRIC_V2_ENABLED=1
```

## API

- `POST /api/v1/runtime/context-rehydration/rehydrate`

Trace: `context_rehydrated` → `memory-fabric-v2:runtime`

Operator page: `/context-rehydration`

Integrates with episodic replay and semantic memory linkage.
