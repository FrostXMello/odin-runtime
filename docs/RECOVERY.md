# Recovery

Odin v0.37 extends stability and self-healing for long uptime.

## Recovery report

`GET /api/v1/runtime/recovery-report` aggregates:

- Runtime guardian state
- Self-healing repairs
- Daemon uptime and restarts

## Safe boot

`POST /api/v1/runtime/recovery/safe-boot` enters degraded safe mode:

- Disables heavy background subsystems
- Minimal model loading
- Preserves mission and approval semantics

## Deployment restore

Restore from snapshot via `POST /api/v1/runtime/deployment/restore`.

## Trace kinds

- `recovery_completed`
- `snapshot_restored`
- `daemon_restarted`

Channel: `diagnostics:runtime`
