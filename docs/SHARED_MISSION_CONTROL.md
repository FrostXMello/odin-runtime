# Shared Mission Control

`core/shared_mission_control/` — shared mission DAGs, objective routing, and ownership transfer.

App handle: `app.shared_mission_control`

## Enable

```env
ODIN_SHARED_MISSION_CONTROL_ENABLED=1
```

## API

- `POST /api/v1/runtime/shared-mission-control/create`
- `POST /api/v1/runtime/shared-mission-control/transfer`
- `GET /api/v1/runtime/shared-mission-control`
- `GET /api/v1/runtime/shared-command`

## Channel

`shared-mission-control:runtime`

## Trace kinds

- `shared_mission_created`
- `mission_control_transferred`

Integrates with `mission_command` and `unified_command_center`. Supports collaborative DAG virtualization and operator pressure maps.
