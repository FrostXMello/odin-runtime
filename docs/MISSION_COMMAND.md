# Mission Command

`core/mission_command/` — mission-centric cognition and operational phase transitions.

App handle: `app.mission_command`

## Enable

```env
ODIN_MISSION_COMMAND_ENABLED=1
```

## Phases

`planning`, `execution`, `recovery`, `stabilization`, `overnight`, `supervision_review`

## API

- `GET /api/v1/runtime/mission-command`
- `POST /api/v1/runtime/mission-command/phase`
- `GET /api/v1/runtime/mission-command/pressure`
- `GET /api/v1/runtime/mission-phases`

## Channel

`mission-command:runtime`

## Trace kinds

- `mission_phase_transitioned`
- `objective_graph_synchronized`

Integrates with `objective_management`, `mission_graph`, `mission_continuity`.

Operator-controlled phase transitions. DAG virtualization (500 node cap). Approval-gated objectives.
