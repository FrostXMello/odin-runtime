# Live Overlays V2

`core/live_overlays_v2/` — floating cognitive overlay system.

App handle: `app.live_overlays_v2`

## Enable

```env
ODIN_LIVE_OVERLAYS_V2_ENABLED=1
ODIN_OVERLAY_MODE=adaptive
```

Overlay types: `reasoning_pulse`, `engineering_assistant`, `memory_recall`, `interruption_warning`, `focus_timer`, `overnight_summary`.

## API

- `GET /api/v1/runtime/live-overlays-v2`
- `POST /api/v1/runtime/live-overlays-v2/attach`
- `POST /api/v1/runtime/live-overlays-v2/suppress`
- `POST /api/v1/runtime/live-overlays-v2/context`

## Channel

`live-overlays-v2:runtime`

## Trace kinds

- `overlay_context_updated`
- `overlay_suppressed`

Adaptive FPS scaling, overlay throttling, focus-aware suppression. No hidden overlays.
