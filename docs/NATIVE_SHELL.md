# Native Shell

`core/native_shell/` — persistent desktop cognitive shell.

## Capabilities

- Platform adapters (Windows, macOS, Linux)
- Workspace command palette and quick actions
- Dock/tray integration metadata
- Session bar with mission summaries
- Live runtime notifications

## Enable

```env
ODIN_NATIVE_SHELL_ENABLED=1
ODIN_NATIVE_DESKTOP_MODE=balanced
```

## API

- `GET /api/v1/runtime/native-shell`
- `POST /api/v1/runtime/native-shell/activate`

Channel: `shell:runtime`
