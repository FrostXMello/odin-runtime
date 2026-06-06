# Unified Command Center

`core/unified_command_center/` — unified runtime coordination and global operational health.

App handle: `app.unified_command_center`

## Enable

```env
ODIN_UNIFIED_COMMAND_CENTER_ENABLED=1
ODIN_COMMAND_PROFILE=balanced
```

## API

- `GET /api/v1/runtime/unified-command/status`
- `POST /api/v1/runtime/unified-command/synchronize`
- `POST /api/v1/runtime/unified-command/initialize`
- `GET /api/v1/runtime/operational-health`
- `GET /api/v1/runtime/global-pressure`

## Channel

`unified-command:runtime`

## Trace kinds

- `command_center_initialized`
- `runtime_layers_synchronized`
- `global_operational_health_updated`

Integrates with `predictive_governance`, `distributed_execution`, `live_orchestration`, `execution_system`, `autonomous_coordination`, `unified_cognitive_core`, `cognitive_scheduler`, `governance_visualization`, `desktop_attention`.

Operator-supervised. Bounded synchronization. Transparent health tracking.
