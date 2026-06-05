# Resource Survival (v0.35)

Consumer-hardware survival modes for GTX 1650 Ti class GPUs and 16GB RAM laptops.

## Modes

- `ultra_light` — minimal VRAM, single model
- `balanced` — default daily use
- `performance` — higher throughput when thermals allow
- `overnight_daemon` — long idle compaction profile

## Configuration

```env
ODIN_RESOURCE_OPTIMIZATION_ENABLED=true
ODIN_SURVIVAL_MODE=balanced
```

## API

- `POST /api/v1/runtime/resource-optimization/survive`
