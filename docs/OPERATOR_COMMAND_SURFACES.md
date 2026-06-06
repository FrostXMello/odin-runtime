# Operator Command Surfaces

`core/operator_command_surfaces/` — unified command HUD and cinematic operational rendering.

App handle: `app.operator_command_surfaces`

## Enable

```env
ODIN_OPERATOR_COMMAND_SURFACES_ENABLED=1
ODIN_COMMAND_PROFILE=balanced
```

## API

- `POST /api/v1/runtime/operator-command-surfaces/render`
- `GET /api/v1/runtime/operator-command-surfaces/layout`
- `GET /api/v1/runtime/command-surfaces`

## Channel

`operator-command-surfaces:runtime`

## Trace kinds

- `command_surface_rendered`
- `operational_overlay_updated`

Profiles: `compact`, `balanced`, `immersive`, `cinematic`, `overnight_command`.

Visual density throttling (max 56 renders). Lazy HUD hydration. Low-power cinematic mode.
