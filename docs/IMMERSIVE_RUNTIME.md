# Immersive Runtime

Prompt 45 ties native shell, voice desktop, visualization, and overlays into immersive cognitive modes.

## Voice Desktop

`core/voice_desktop/` — `VoiceDesktopCoordinator`

```env
ODIN_VOICE_DESKTOP_ENABLED=1
ODIN_REALTIME_VOICE_ENABLED=1
```

Modes: `passive` · `assistant` · `immersive` · `daemon`

API:

- `POST /api/v1/runtime/voice-desktop/listen`
- `POST /api/v1/runtime/voice-desktop/interrupt`

Trace: `voice_interrupt_detected` → `voice:runtime`

## Immersive Modes

| Mode | FPS cap | Use |
|------|---------|-----|
| compact | 15 | Low-power daemon |
| balanced | 30 | Daily driver |
| immersive | 45 | Live reasoning |
| cinematic | 60 | Full visualization |

Set via `POST /api/v1/runtime/desktop-client/mode` or `ODIN_NATIVE_DESKTOP_MODE`.

## Operator Console Pages

- `/desktop`
- `/conversation-workspace`
- `/visualization`
- `/operator-experience`
- `/live-memory`
- `/evolution-review`
- `/workspace-restore`

## Resource Constraints

- Stream throttling on visualization channels
- Lazy graph rendering
- VRAM-aware defaults
- Low-power daemon mode via voice `daemon` + desktop `compact`

All immersive features remain supervised, approval-gated, and reversible.
