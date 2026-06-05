# Strategic Reasoning Engine (Prompt 32)

Multi-step strategic planning with assumptions, uncertainty, and causal justification.

## Enable

```env
strategic_reasoning_enabled=true
```

Default: disabled. All outputs include assumptions, uncertainty, confidence, causal justification, and knowledge references.

## Architecture

| Module | Purpose |
|--------|---------|
| `strategic_runtime.py` | Main orchestrator |
| `recursive_planning.py` | Multi-step plan decomposition |
| `long_horizon_objectives.py` | Persistent objective chains |
| `economic_reasoning.py` | Resource balancing |
| `systems_reasoning.py` | Systems-level analysis |
| `risk_projection.py` | Probabilistic risk scoring |
| `geopolitical_reasoning.py` | Bounded scenario assessment |

## Output schema

Every analysis includes:
- `assumptions` — explicit constraints (local-first, operator-supervised)
- `uncertainty` — quantified doubt
- `confidence` — aggregate score
- `causal_justification` — reasoning chain label
- `knowledge_references` — facts from knowledge fabric

## APIs

- `GET /api/v1/runtime/strategy`
- `POST /api/v1/runtime/strategy/analyze`
- `GET /api/v1/missions/{id}/strategy`

## Streaming

**Channel:** `strategy:runtime`

**Trace kind:** `strategy_generated`

## Operator Console

`/runtime/strategy`

## Integration

- Reads from `knowledge_runtime` for supporting references
- Complements `world_simulation` for projection and prediction
- Federation layer can delegate cross-node strategic analysis
