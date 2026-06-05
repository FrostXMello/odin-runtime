# Milestone 7 — ODIN Cognitive Kernel

## Architecture shift

**FROM:** Distributed intelligent subsystems acting independently  
**TO:** One cognitive kernel; subsystems are signal producers only

## Flow

```
Subsystem → publish(Event) → SignalUnificationBus
  → OdinCognitiveKernel.process_signal
  → GlobalContextGraph.apply_signal
  → CognitivePriorityEngine.rank
  → CognitiveState updated

Tool execute → ExecutionGovernor.evaluate → APPROVE?
  → Policy + Trust + Heimdall → RuntimeToolExecutor
```

## Modules (`odin_backend/core/`)

| Module | Path | Role |
|--------|------|------|
| Signal Bus | `bus/` | Event → Signal → kernel → inner bus |
| Kernel | `kernel/` | Global state, conflict resolution |
| Context Graph | `context_graph/` | Unified system truth |
| Priority | `priority/` | Strict top-10 ranking |
| Governor | `governor/` | Final execution gate |

## API

- `GET /api/v1/kernel/state` — CognitiveState
- `GET /api/v1/kernel/priority`
- `GET /api/v1/kernel/graph`
- `GET /api/v1/kernel/governor/decisions`
- `POST /api/v1/kernel/governor/preview`

## Rules enforced

- No tool execution without governor approval
- All publishes pass through kernel via `SignalUnificationBus`
- No isolated subsystem truth — graph updated on every signal

## Tests

```powershell
cd odin\backend
$env:PYTHONPATH=".\"
.\.venv\Scripts\python -m pytest tests/test_milestone7.py -v
```
