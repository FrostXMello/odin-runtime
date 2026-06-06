# Governance Visualization

`core/governance_visualization/` — governance HUD and cinematic rendering.

App handle: `app.governance_visualization`

## Enable

```env
ODIN_GOVERNANCE_VISUALIZATION_ENABLED=1
```

## API

- `POST /api/v1/runtime/governance-visualization/render`
- `GET /api/v1/runtime/governance-visualization`

## Channel

`governance-visualization:runtime`

## Trace kinds

- `governance_surface_rendered`

Lazy visualization hydration. Render throttling (max 48). Low-power governance mode.
