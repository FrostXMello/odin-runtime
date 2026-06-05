# Odin Real Execution Engine

## Architecture

```
POST /executions/run
        ↓
ExecutionEngine.submit()
        ↓
ExecutorRegistry (capability → executor)
        ↓
ExecutionSandbox + subprocess / workflow
        ↓
StreamBuffer (stdout/stderr) + CausalTracer + StreamBridge
        ↓
Operator Console (/executions, live WS)
```

### Modules (`core/execution/`)

| File | Role |
|------|------|
| `engine.py` | Orchestration: allocate, run, cancel, retry, recovery |
| `executor.py` | Python, shell, file, workflow, internal API executors |
| `registry.py` | Capability-based executor registration |
| `sandbox.py` | Command allowlist, path traversal block, python guards |
| `stdout.py` | Ring buffers for stdout/stderr |
| `result_store.py` | In-memory execution records |
| `leases.py` | Lease expiry for stuck detection |
| `cancellation.py` | Cancel tokens + task binding |
| `recovery.py` | Background orphan/stuck sweep |
| `metrics.py` | Throughput and counters |
| `contract.py` | Existing governor tool pipeline (unchanged) |

Mission `ExecutionDispatcher` and `MissionRuntime` are **not** replaced; this engine is for explicit real work via API (and future mission task wiring).

## Lifecycle

`QUEUED → ALLOCATED → RUNNING → COMPLETED | FAILED | CANCELLED | TIMED_OUT`

Also: `RETRYING`, `ROLLING_BACK`, `WAITING`

## API

- `POST /api/v1/executions/run`
- `GET /api/v1/executions/{id}`
- `GET /api/v1/executions/{id}/logs`
- `POST /api/v1/executions/{id}/cancel`
- `POST /api/v1/executions/{id}/retry`
- `GET /api/v1/runtime/executions`
- `WS /api/v1/ws/executions/{id}`

## Demo

```bash
curl -X POST http://127.0.0.1:8000/api/v1/executions/run \
  -H "Content-Type: application/json" \
  -d '{"capability":"python.safe","params":{"code":"print(42)"}}'
```

Open Operator → **Executions** for live stdout and controls.
