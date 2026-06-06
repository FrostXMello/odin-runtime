# Desktop Client

`frontend/desktop_client/` — React + TypeScript cognitive desktop shell integrated with the existing Electron bridge.

## Modules

| Module | Role |
|--------|------|
| `shell/` | Window modes, tray, immersive navigation |
| `workspace/` | Unified conversation workspace layout |
| `cognition/` | Live reasoning panels |
| `streaming/` | Runtime WebSocket synchronizer |
| `overlays/` | Floating HUD surfaces |
| `voice/` | Push-to-talk + subtitles |
| `memory/` | Thread explorer |
| `missions/` | Mission control HUD |
| `agents/` | Agent society visualization |
| `evolution/` | Self-development review |

## Backend

`core/desktop_client/` — `DesktopClientRuntime` with local session persistence.

## Enable

```env
ODIN_DESKTOP_CLIENT_ENABLED=1
```

## API

- `GET /api/v1/runtime/desktop-client`
- `POST /api/v1/runtime/desktop-client/connect`
- `POST /api/v1/runtime/desktop-client/mode`

## Modes

`compact` · `balanced` · `immersive` · `cinematic` — adaptive FPS caps (15–60).

## Traces

`desktop_session_restored` → `desktop:runtime`

## Run

```bash
cd frontend
npm run electron:dev
```

The desktop client connects to the local Odin backend at `127.0.0.1:8000`.
