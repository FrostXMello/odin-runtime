# Immersive Runtime

`core/immersive_ui/` — adaptive cognitive interface modes.

## Modes

`minimal`, `balanced`, `immersive`, `cinematic`

FPS caps: 15 / 30 / 45 / 60 — GPU-safe for GTX 1650 Ti.

## API

- `GET /api/v1/runtime/immersive`
- `POST /api/v1/runtime/immersive/mode`

Trace: `immersive_mode_changed` → `immersive:runtime`
