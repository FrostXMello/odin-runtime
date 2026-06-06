# Regression Management

Regression detection across benchmarks and patch pipeline.

## Detection

- Benchmark suite compares consecutive latency snapshots (>15% degradation)
- Patch pipeline flags benchmark delta < -5%
- Outcomes persisted in `self_improvement_memory.regression_memory`

## Response

1. Emit `regression_detected`
2. Trigger `rollback_triggered` when patch regression confirmed
3. Record in SQLite for future cycle avoidance

## Operator UI

- `/runtime/regressions` — regression inspector
- `/runtime/performance-drift` — benchmark drift timeline

## Channel

`regressions:runtime`
