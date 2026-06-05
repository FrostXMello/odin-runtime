# Multimodal Operator Intelligence (Prompt 28)

Odin Runtime extends local operator intelligence with multimodal perception, desktop awareness, screen understanding, voice, copilot assistance, and human collaboration — all local-first and opt-in.

## Enable

```env
multimodal_perception_enabled=true
desktop_awareness_enabled=true
voice_enabled=true
copilot_mode=suggestion
```

Default: all disabled except `copilot_mode=passive_observer`.

## Modules

| Layer | Path | App attribute |
|-------|------|---------------|
| Perception | `core/perception/` | `multimodal_perception` |
| Desktop | `core/desktop/` | `desktop_monitor` |
| Vision | `core/vision/` | `screen_pipeline` |
| Voice | `core/voice/` | `voice_runtime` |
| Copilot | `core/copilot/` | `copilot_runtime` |
| Workspace memory | `core/copilot/workspace_memory.py` | `workspace_memory` |
| Collaboration | `core/collaboration/` | `collaboration_runtime` |

## APIs

- `GET /api/v1/runtime/perception`
- `GET /api/v1/runtime/desktop`
- `POST /api/v1/runtime/desktop/ingest`
- `GET /api/v1/runtime/workspace`
- `GET /api/v1/runtime/copilot`
- `POST /api/v1/runtime/copilot/tick`
- `GET /api/v1/runtime/voice`
- `POST /api/v1/runtime/voice/start` / `stop`
- `POST /api/v1/runtime/snapshot`
- `GET /api/v1/runtime/screenshots`
- `GET /api/v1/runtime/collaboration`
- `POST /api/v1/runtime/approval/{id}`

## Operator Console

- `/runtime/perception` — unified context stream
- `/runtime/desktop` — active window timeline
- `/runtime/voice` — voice session monitor
- `/runtime/copilot` — suggestions and predictions
- `/runtime/workspace` — learned patterns
- `/runtime/collaboration` — approval queue

## Safety

- Desktop awareness is permission-controlled and toggleable
- Clipboard content is privacy-filtered (passwords/tokens redacted)
- Interaction maps are read-only — no unrestricted UI automation
- Copilot suggestions require supervised modes for execution
- Approval flows gate sensitive actions

## Streaming channels

`perception:runtime`, `desktop:runtime`, `voice:runtime`, `copilot:runtime`, `workspace:runtime`, `collaboration:runtime`
