# Autonomous Activity Stream

Live autonomous activity across native OS, autonomous loop V2, and engineering evolution V2.

## API

- `GET /api/v1/runtime/autonomous-activity`
- `GET /api/v1/runtime/reasoning-pulse`

Channels: `autonomous-loop-v2:runtime`, `native-os:runtime`, `desktop-v2:runtime`

Operator pages: `/autonomous-activity`, `/reasoning-pulse`

Frontend: `frontend/cognitive_workspace/src/desktop_v2/DesktopV2Panels.tsx` — `AutonomousActivityStream`, `ReasoningPulse`

GPU-safe with adaptive FPS caps and stream compression.
