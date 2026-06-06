# Runtime Fusion

`core/runtime_fusion/` — cross-runtime state fusion and checkpoint convergence.

App handle: `app.runtime_fusion`

## Enable

```env
ODIN_RUNTIME_FUSION_ENABLED=1
ODIN_OPERATIONAL_CONTINUITY_MODE=balanced
```

## API

- `GET /api/v1/runtime/runtime-fusion`
- `POST /api/v1/runtime/runtime-fusion/fuse`
- `POST /api/v1/runtime/runtime-fusion/restore`

## Channel

`runtime-fusion:runtime`

## Trace kinds

- `runtime_contexts_fused`
- `cross_runtime_pressure_stabilized`

Integrates with `context_synchronization`, `execution_system`, `runtime_stabilization`.

Reversible checkpoints. Fusion cooldown scheduling (max 48 loops). Cross-layer stabilization.
