# Live Copilot

Real-time engineering assistance with supervised modes.

## Modes

| Mode | Behavior |
|------|----------|
| passive | Observe only |
| suggestive | Contextual hints |
| collaborative | Active guidance |
| supervised-action | Requires approval |

## API

- `GET /api/v1/runtime/live-copilot`
- `POST /api/v1/runtime/live-copilot/assist`

Trace: `realtime_assistance_generated` on `live-copilot:runtime`.
