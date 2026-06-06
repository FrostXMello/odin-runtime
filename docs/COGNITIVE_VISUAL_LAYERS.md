# Cognitive Visual Layers

`core/cognitive_visual_layers/` — cinematic cognition rendering.

App handle: `app.cognitive_visual_layers`

## Enable

```env
ODIN_COGNITIVE_VISUAL_LAYERS_ENABLED=1
ODIN_COGNITIVE_RENDER_MODE=adaptive
ODIN_VISUAL_DENSITY=balanced
```

Modes: `compact`, `balanced`, `immersive`, `cinematic`, `overnight_autonomous`.

## API

- `GET /api/v1/runtime/cognitive-visual-layers`
- `POST /api/v1/runtime/cognitive-visual-layers/constellation`
- `POST /api/v1/runtime/cognitive-visual-layers/river`

## Channel

`visual-layers:runtime`

## Trace kinds

- `runtime_constellation_rendered`
- `objective_river_rendered`
- `cognitive_visual_density_compressed`

Adaptive render scaling, lazy visual hydration, low-power cinematic mode.
