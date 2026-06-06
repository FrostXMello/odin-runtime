# Immersive Operator Experience

Prompt 46 immersive UX spans `frontend/cognitive_workspace/immersive/` and operator console pages.

## Immersive surfaces

- Animated cognition surfaces
- Live mission map
- Agent constellation
- Memory pulse animations
- Attention field visualization
- Voice-reactive overlays
- Cinematic focus transitions

## Operator productivity

`core/operator_productivity/` — focus cycles, distraction detection, daily strategy.

```env
ODIN_OPERATOR_PRODUCTIVITY_ENABLED=1
```

API: `/api/v1/runtime/operator-productivity/*`

Channel: `productivity:runtime`

Trace: `operator_focus_degraded`

## Operator pages

| Path | Purpose |
|------|---------|
| `/workspace` | Unified cognitive workspace |
| `/reasoning-live` | Live reasoning surface |
| `/conversations` | Conversational presence |
| `/evolution-review` | Supervised upgrades |
| `/cognitive-daemon` | Continuous cognition |
| `/operator-productivity` | Focus & energy |
| `/attention-map` | Confidence heatmap |
| `/live-memory` | Memory threads |
| `/mission-playback` | Cognition timeline |
| `/upgrade-timeline` | Patch history |

## Performance safeguards

FPS caps · adaptive degradation · lazy rendering · stream batching · ultra_light profile

All immersive features remain approval-gated and locally supervised.
