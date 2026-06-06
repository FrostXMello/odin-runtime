# Overlay System

`core/desktop_overlay/` — floating local-only UI surfaces.

## Overlays

| Kind | Purpose |
|------|---------|
| `terminal` | Terminal assistant |
| `debug` | Debugging overlay |
| `mission_hud` | Mission HUD |
| `subtitles` | Live voice subtitles |
| `memory_hint` | Memory recall hints |
| `workflow` | Workflow suggestions |

## Enable

```env
ODIN_DESKTOP_OVERLAY_ENABLED=1
```

## API

- `POST /api/v1/runtime/desktop-overlay/attach`
- `GET /api/v1/runtime/desktop-overlay/memory-surface`

Integrates with `live_overlay` for composited panels.

## Requirements

Movable · transparent · GPU-light · local-only.

## Traces

`overlay_attached` → `overlay:runtime`, `desktop:runtime`

`memory_surface_rendered` → `memory-threads:runtime`, `visualization:runtime`
