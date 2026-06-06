# Live Reasoning Surface

`core/live_reasoning/` — token-level streaming reasoning visualization.

## Modules

- `reasoning_surface.py` — `LiveReasoningRuntime` (`app.live_reasoning`)
- `token_stream_visualizer.py` — chunked token streams
- `reasoning_layers.py` — layered cognition stack
- `attention_heatmap.py` — confidence heatmaps
- `live_chain_tracker.py` — inference chains
- `cognitive_diff.py` — branch comparisons
- `reasoning_timeline.py` — mission playback timeline

## Enable

```env
ODIN_LIVE_REASONING_ENABLED=1
```

## API

- `POST /api/v1/runtime/reasoning-live/render`
- `POST /api/v1/runtime/reasoning-live/profile`

## Channel

`reasoning-live:runtime`

## Traces

`reasoning_branch_rendered` → `reasoning-live:runtime`, `reasoning-streams:runtime`

## Performance

Lazy rendering, FPS caps per resource profile, VRAM-safe defaults.
