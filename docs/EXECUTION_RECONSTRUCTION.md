# Execution Reconstruction

`core/execution_reconstruction/` — bounded execution state reconstruction and workspace continuity replay.

App handle: `app.execution_reconstruction`

## Enable

```env
ODIN_EXECUTION_RECONSTRUCTION_ENABLED=1
```

## API

- `POST /api/v1/runtime/execution-reconstruction/reconstruct`
- `POST /api/v1/runtime/execution-reconstruction/restore`
- `POST /api/v1/runtime/execution-reconstruction/simulate`
- `POST /api/v1/runtime/execution-reconstruction/rebuild`

## Channel

`execution-reconstruction:runtime`

## Trace kinds

- `execution_state_reconstructed`
- `workspace_sequence_rebuilt`
- `cognition_window_restored`
- `execution_restore_simulated`

Bounded reconstruction loops (max 40). Approval-gated restoration via `operator_veto`. No unsafe replay mutation — simulate-only restore path.
