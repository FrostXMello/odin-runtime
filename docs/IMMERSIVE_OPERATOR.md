# Immersive Operator Console

Prompt 41 operator pages for the cognitive interface layer.

## Pages

| Route | Purpose |
|-------|---------|
| `/runtime/presence` | Embodied presence and mood |
| `/runtime/cognition-live` | Live cognition viewport |
| `/runtime/thought-stream` | Streaming thought pipeline |
| `/runtime/live-overlay` | Workspace overlay modes |
| `/runtime/conversation` | Conversational runtime status |
| `/runtime/personality` | Personality projection |
| `/runtime/self-development` | Supervised improvement queue |
| `/runtime/reasoning-map` | Live reasoning layers |
| `/runtime/memory-activity` | Memory activity map |

## UX goals

- WebSocket-driven refresh via existing runtime stream
- Dark-mode optimized cards
- Low-latency polling (4–12s per page)
- Keyboard-navigable shell sidebar

## Resource modes

Set `ODIN_COGNITIVE_INTERFACE_MODE` to control UI framerate and GPU idle release:

- `minimal` — 15 FPS target, lightweight visualization
- `balanced` — 30 FPS (default)
- `immersive` — 45 FPS, progressive rendering
- `cinematic` — 60 FPS, full visualization
