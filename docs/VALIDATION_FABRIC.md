# Validation Fabric

Confidence-gated patch validation and engineering quality scoring.

## Capabilities

- Isolated test runner
- Regression matrix
- Patch benchmarking
- Runtime safety checks
- Confidence gates
- Rollback recommendations

## API

- `GET /api/v1/runtime/testing`
- `POST /api/v1/runtime/testing/validate-patch`

Patches failing confidence gates require operator approval.

Trace: `regression_detected` on `testing:runtime`.
