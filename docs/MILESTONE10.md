# Milestone 10 — Runtime Conscious Loop

## Objective

ODIN runs as a **persistent cognitive system** with a continuous ingest → interpret → prioritize → plan → coherence → govern → execute → observe → memory → stability cycle.

## Component

| Path | Role |
|------|------|
| `core/conscious_loop/loop.py` | `RuntimeConsciousLoop` — perpetual + single `run_cycle()` |
| `core/conscious_loop/planner.py` | `SelfReasoningPlanner` — merge/split/reprioritize TaskGraph |
| `core/conscious_loop/decisions.py` | `CycleDecision` — ALLOW / ESCALATE / DEFER / OBSERVE |

## Cycle steps

1. **Ingest** — `active_signals`, queued tasks, system tick signal  
2. **Interpret** — kernel `process_signal`  
3. **Prioritize** — `CognitivePriorityEngine.rank()`  
4. **Plan** — self-reasoning on TaskGraph  
5. **Coherence** — validate before execution  
6. **Governance** — autonomy + coherence gate  
7. **Execute** — ready nodes via execution contract (governor-gated)  
8. **Observe** — collect results  
9. **Memory** — store outcomes  
10. **Stability** — every `conscious_loop_stability_interval` ticks only  

## Autonomy behavior

| Level | Loop behavior |
|-------|----------------|
| 0–1 | OBSERVE only |
| 2 | Plan/prepare only |
| 3+ | ALLOW when coherent + ready nodes |

## Config (`ODIN_` prefix)

```
conscious_loop_enabled=true
conscious_loop_interval_seconds=3.0
conscious_loop_stability_interval=10
conscious_loop_max_executions_per_cycle=2
```

## API

- `GET /api/v1/conscious-loop/status`
- `POST /api/v1/conscious-loop/tick` — manual single cycle
- `GET /api/v1/conscious-loop/escalations`

## Safety

- Governor + execution contract required for tool runs  
- Coherence conflicts → ESCALATE (no execution)  
- Stability loop emits corrective signals only  
- Kernel remains sole CognitiveState writer  

## Tests

```powershell
cd odin\backend
$env:PYTHONPATH="...\odin\backend"
.\.venv\Scripts\python -m pytest tests/test_milestone10.py -v
```
