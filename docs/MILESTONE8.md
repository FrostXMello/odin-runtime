# Milestone 8 — Cognitive Stability Layer

## Flow (updated)

```
Signal → SignalUnificationBus → Kernel
  → PriorityEngine
  → CoherenceEngine
  → CognitiveState
Execution → Governor
  → Coherence gate (score threshold)
  → AutonomyLayer
  → Policy + Trust + Heimdall
  → Execute
StabilityLoop → corrective signals only (no direct mutation)
```

## Modules

| Module | Path | Purpose |
|--------|------|---------|
| Coherence | `core/coherence/` | Consistency score, conflicts, resolutions |
| Snapshots | `core/snapshot/` | Full state capture, restore, diff |
| Stability loop | `core/stability/` | Periodic self-audit |
| Memory refinement | `memory/refinement/` | Traceable merge/compress |
| Autonomy | `core/autonomy/` | Levels 0–4, scoped grants |

## Autonomy levels

- **0** — read-only
- **1** — suggestions only (default)
- **2** — pre-approved workflows
- **3** — bounded safe tools + governor
- **4** — supervised with explicit confirmation

## API (`/api/v1/stability`)

- `GET /coherence`
- `POST /snapshots`
- `POST /stability-loop`
- `POST /memory/refine`
- `GET/PATCH /autonomy`

## Principles

- Consistency over completeness
- No destructive memory delete — archive + trace log
- Stability loop never bypasses kernel or governor

## Tests

```powershell
cd odin\backend
$env:PYTHONPATH=".\"
.\.venv\Scripts\python -m pytest tests/test_milestone8.py -v
```
