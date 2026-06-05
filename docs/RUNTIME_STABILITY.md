# Runtime Stability (v0.35)

The stability engine keeps Odin dependable during long-running local operation.

## Modules

- `core/stability/runtime_guardian.py` — orchestrator (`app.runtime_guardian`)
- `core/stability/health_supervisor.py` — health evaluation
- `core/stability/watchdog_runtime.py` — stalled loop detection
- `core/stability/state_checkpointing.py` — runtime snapshots and rollback
- `core/stability/crash_recovery.py` — post-crash restoration
- `core/stability/runtime_repair.py` — orphan cleanup and repair
- `core/stability/emergency_recovery.py` — emergency degraded recovery

## Configuration

```env
ODIN_RUNTIME_GUARDIAN_ENABLED=true
```

## APIs

- `GET /api/v1/runtime/stability`
- `POST /api/v1/runtime/stability/supervise`
- `POST /api/v1/runtime/stability/recover`
- `POST /api/v1/runtime/stability/emergency`
