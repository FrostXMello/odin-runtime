# Cognitive Workspace

`core/cognitive_workspace/` — unified adaptive cognitive operating surface.

## Modules

- `workspace_runtime.py` — orchestrator (`app.cognitive_workspace`)
- `layout_engine.py` — draggable panel layouts
- `workspace_state.py` / `session_layouts.py` — persistent layouts
- `attention_router.py` — focus routing
- `cognitive_focus.py` — immersive / fullscreen modes
- `live_panels.py` — mission + agent live data

## Modes

`minimal` · `operator` · `engineering` · `immersive` · `cinematic`

## Resource profiles

`ultra_light` · `balanced` · `immersive` · `cinematic`

## Enable

```env
ODIN_COGNITIVE_WORKSPACE_ENABLED=1
```

## API

- `POST /api/v1/runtime/cognitive-workspace/open`
- `POST /api/v1/runtime/cognitive-workspace/mode`
- `POST /api/v1/runtime/cognitive-workspace/profile`

## Frontend

`frontend/cognitive_workspace/` — adaptive shell, draggable panels, command palette.

## Traces

`workspace_focus_changed`, `cognitive_transition_rendered` → `workspace:runtime`
