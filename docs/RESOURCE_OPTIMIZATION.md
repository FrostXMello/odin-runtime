# Resource Optimization Runtime (v0.34)

This runtime stabilizes Odin on consumer hardware by adapting model loading and cognition quality to RAM, VRAM, thermal, and battery constraints.

## Modules

- `core/resource_optimization/adaptive_loading.py` — adaptive model load policy.
- `core/resource_optimization/memory_pressure_runtime.py` — RAM/VRAM pressure evaluation.
- `core/resource_optimization/model_swapper.py` — active model swap and downgrade policy.
- `core/resource_optimization/idle_compaction.py` — idle-time memory compaction.
- `core/resource_optimization/lightweight_modes.py` — lightweight/degraded/minimal modes.
- `core/resource_optimization/battery_aware_runtime.py` — battery-aware throttling.
- `core/resource_optimization/resource_runtime.py` — orchestrator mounted as `app.resource_optimization`.
