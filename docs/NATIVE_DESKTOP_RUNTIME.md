# Native Desktop Runtime

`core/native_desktop/` — native autonomous desktop persistence layer.

App handle: `app.native_desktop`

## Enable

```env
ODIN_NATIVE_DESKTOP_ENABLED=1
ODIN_DESKTOP_PROFILE=balanced
```

Profiles: `compact`, `balanced`, `immersive`, `engineering`, `overnight`.

## API

- `GET /api/v1/runtime/native-desktop/status`
- `POST /api/v1/runtime/native-desktop/initialize`
- `POST /api/v1/runtime/native-desktop/restore`
- `POST /api/v1/runtime/native-desktop/notify`
- `POST /api/v1/runtime/native-desktop/low-power`

## Channel

`native-desktop:runtime`

## Trace kinds

- `desktop_runtime_initialized`
- `native_notification_dispatched`

Integrates with `native_os`, `workspace_sessions`, `cognitive_daemon_v2`.

Local-first. Operator-controlled tray actions. Low-power mode with bounded cognition.
