# Performance Profiles

Odin v0.37 performance layer targets daily-driver hardware:

- **16 GB RAM**
- **GTX 1650-class GPUs (4 GB VRAM)**
- **Apple Silicon M-series**
- **CPU-only fallback**

## Profiles

| Profile | Use case |
|---------|----------|
| `ultra_light` | Minimal VRAM, fast responses |
| `balanced` | Default daily driver |
| `performance` | Heavier reasoning when resources allow |
| `overnight` | Background cognition, low operator load |

## API

- `GET /api/v1/runtime/performance` — snapshot
- `POST /api/v1/runtime/performance/optimize` — pressure-aware optimization
- `POST /api/v1/runtime/performance/startup` — startup plan

## Local AI modes

Set inference chain via `POST /api/v1/runtime/local-ai/mode` with `{ "mode": "balanced" }`.

## Trace channels

Performance events stream on `performance:runtime` (memory pressure, model swap, startup optimized).
