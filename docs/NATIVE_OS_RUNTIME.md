# Native OS Runtime

`core/native_os/` — native desktop integration layer.

App handles: `app.native_os`, `app.system_intents`

## Enable

```env
ODIN_NATIVE_OS_ENABLED=1
```

## API

- `GET/POST /api/v1/runtime/native-os/*`
- `POST /api/v1/runtime/system-intents/*`
- `GET /api/v1/runtime/window-state`
- `POST /api/v1/runtime/notifications/send`

## Channel

`native-os:runtime`, `desktop-v2:runtime`

Cross-platform adapters for Windows, macOS, and Linux. Local-first; no unrestricted OS automation.
