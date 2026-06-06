# Model Routing

Odin v0.38 orchestrates local models for daily-driver hardware.

## Strategy

| Task | Model role |
|------|------------|
| Simple / battery | `fast` |
| Coding | `code` |
| Deep reasoning | `reasoning` |

## API

- `GET /api/v1/runtime/model-routing`
- `POST /api/v1/runtime/model-routing/route`
- `POST /api/v1/runtime/reasoning/route`

Features: context compression on battery, memory-bound inference, deep reasoning scheduler.

Trace kind: `model_route_selected` on `reasoning:runtime`.

Target hardware: GTX 1650-class 4GB VRAM, 16GB RAM, Apple Silicon, CPU fallback.
