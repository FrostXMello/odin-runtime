# Runtime Benchmarks

`core/runtime_benchmarks/` — continuous performance measurement.

## Suites

- Cognition, reasoning, latency, memory, engineering, autonomy

## API

- `GET /api/v1/runtime/benchmarks`
- `POST /api/v1/runtime/benchmarks/run`
- `GET /api/v1/runtime/benchmarks/history`
- `GET /api/v1/runtime/performance-drift`

## Traces

- `benchmark_completed` → `benchmarks:runtime`
- `regression_detected` → `benchmarks:runtime`, `regressions:runtime`

History retained in-memory for drift comparison; SQLite outcomes in self-improvement memory.
