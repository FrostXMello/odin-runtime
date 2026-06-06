# Live Visualization

`core/live_visualization/` — GPU-aware cognitive visualization runtime.

## Views

- Reasoning DAG
- Memory activation graph
- Mission execution waves
- Federation topology
- Agent collaboration graph
- Active cognitive surface

## Enable

```env
ODIN_LIVE_VISUALIZATION_ENABLED=1
```

## API

- `POST /api/v1/runtime/live-visualization/render`

## Streaming channels

Uses existing streams:

- `thought-stream:runtime`
- `cognition-live:runtime`
- `reasoning-streams:runtime`
- `society:runtime`
- `federation:runtime`

New: `visualization:runtime`

## Performance

Adaptive FPS scaling tied to `native_desktop_mode`. Lazy graph rendering and VRAM-safe defaults for GTX 1650 Ti / M-series MacBooks.

## Traces

`visualization_synced`, `live_reasoning_rendered` → `visualization:runtime`
