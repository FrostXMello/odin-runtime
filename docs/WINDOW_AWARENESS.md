# Window Awareness

`core/window_awareness/` — local active window and workspace transition tracking.

App handle: `app.window_awareness`

## Enable

```env
ODIN_WINDOW_AWARENESS_ENABLED=1
ODIN_WINDOW_TRACKING_ENABLED=1
```

## API

- `GET /api/v1/runtime/window-awareness/active`
- `GET /api/v1/runtime/window-awareness/workspace`
- `POST /api/v1/runtime/window-awareness/transition`
- `POST /api/v1/runtime/window-awareness/classify`

## Channel

`window-awareness:runtime`

## Trace kinds

- `workspace_transition_detected`
- `active_window_classified`

Classifies: editor, terminal, browser, documentation, communication.

Privacy: configurable exclusions, local-only processing, operator-visible monitoring state.
