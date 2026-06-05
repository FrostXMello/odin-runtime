# Cognitive Economy (Prompt 33)

Bounded cognitive budgeting, token accounting, and compute prioritization.

## Modes

| Mode | Token budget | Model selection |
|------|-------------|-----------------|
| `low_resource` | 5,000 | mock |
| `balanced` | 10,000 | qwen2.5 |
| `high_performance` | 20,000 | deepseek-r1 |

## Features

- Cognitive budgets with spend tracking
- Per-mission token ledger
- Mission value scoring
- Dynamic model selection by cost/complexity
- Resource negotiation between subsystems
- Compute allocation by demand

## APIs

- `GET /api/v1/runtime/economy`
- `GET /api/v1/missions/{id}/economy`

## Streaming

**Channel:** `economy:runtime`  
**Trace kind:** `cognition_budget_updated`

## Safety

Budget exceeded returns `accepted: false`. No hidden overruns. Operator can switch modes at any time.
