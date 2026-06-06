# Timeline Visualization

`core/timeline_visualization/` — cinematic operational timelines and cognition replay rendering.

App handle: `app.timeline_visualization`

## Enable

```env
ODIN_TIMELINE_VISUALIZATION_ENABLED=1
ODIN_TIMELINE_RENDER_MODE=adaptive
```

## API

- `GET /api/v1/runtime/timeline-visualization/render`
- `POST /api/v1/runtime/timeline-visualization/compress`
- `POST /api/v1/runtime/timeline-visualization/synchronize`
- `GET /api/v1/runtime/cognition-timeline`

## Channel

`timeline-visualization:runtime`

## Trace kinds

- `operational_timeline_rendered`
- `timeline_window_compressed`
- `timeline_layers_synchronized`
- `timeline_overlay_generated`

Supported profiles: `compact`, `balanced`, `immersive`, `cinematic`, `overnight_replay`. Adaptive timeline render throttling and lazy hydration.
