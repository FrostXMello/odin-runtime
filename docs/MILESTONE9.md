# Milestone 9 — Internal Data Architecture + Agent Protocol

## Objective

Strict runtime data contracts, single cognitive state source of truth, task graph execution format, universal signals, and ODIN-mediated agent communication.

## Components

| Component | Path | Purpose |
|-----------|------|---------|
| **CognitiveState (SSOT)** | `core/kernel/state.py` | Unified runtime state; kernel-only writes |
| **Signal schema** | `core/bus/signals.py` | Universal event envelope |
| **TaskGraph** | `models/task_graph.py` | Graph-based work (`TaskNode`) |
| **AgentMessage** | `models/agent_message.py` | Agent → ODIN protocol |
| **AgentProtocolHub** | `agents/protocol.py` | No peer-to-peer; ODIN routes all |
| **ExecutionContract** | `core/execution/contract.py` | 9-step traceable pipeline |
| **MemoryItem** | `memory/models.py` | Unified memory schema |
| **KnowledgeGraphNode** | `schemas/graph_node.py` | Strict KG node contract |

## CognitiveState fields

- `active_signals[]`, `task_graph{}`, `priority_queue[]`
- `coherence_snapshot{}`, `autonomy_state{}`, `memory_context{}`
- `active_agents{}`, `execution_log[]`, `system_health{}`
- `last_stability_check`

## Processing flow

```
Signal → Bus → Kernel (writes CognitiveState)
  → Priority → Coherence (+ TaskGraph linkage)
  → Governor (ESCALATE on conflicts)
  → Autonomy → ExecutionContract → Tool → Memory → Stability audit
```

## API (`/api/v1/protocol`)

- `GET /state/schema` — full cognitive state
- `GET /task-graph` — task graph snapshot
- `POST /agent/message` — inbound agent report
- `POST /agent/assign` — ODIN → agent assignment
- `POST /execution/pipeline` — full execution contract run
- `POST /tasks/submit` — orchestrator task + graph node

## Rules enforced

1. Only `OdinCognitiveKernel` commits `CognitiveState`
2. Agents are stateless executors; messages target `to_odin=True`
3. All work traceable via `TaskGraph`
4. Coherence conflicts → `ESCALATE_TO_USER` (no silent execution)
5. Stability loop emits signals only; records `last_stability_check` on kernel

## Tests

```powershell
cd odin\backend
$env:PYTHONPATH="c:\Users\Gagan\Downloads\Projects\Odin\odin\backend"
.\.venv\Scripts\python -m pytest tests/test_milestone9.py tests/ -q
```
