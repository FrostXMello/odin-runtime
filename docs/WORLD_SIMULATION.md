# Persistent World Simulation (Prompt 32)

Odin maintains a **bounded internal world model** for long-term reasoning, prediction, and strategic planning.

## Enable

```env
world_simulation_enabled=true
simulation_max_branches=5
```

Default: disabled. Simulations are observable, confidence-scored, and reversible. No hidden autonomous execution.

## Architecture

| Module | Purpose |
|--------|---------|
| `world_runtime.py` | Orchestrator |
| `world_state.py` | SQLite entity/relationship/timeline store |
| `causal_world_graph.py` | Causal links and effect prediction |
| `simulation_engine.py` | Bounded branching scenarios |
| `prediction_engine.py` | Mission outcome prediction |
| `scenario_planner.py` | Multi-step scenario planning |
| `uncertainty_engine.py` | Confidence/uncertainty quantification |

SQLite tables: `odin_world_entities`, `odin_world_relationships`, `odin_world_timelines`.

## Capabilities

- Hypothetical simulation with branching futures (max 5 branches)
- Mission outcome prediction with uncertainty maps
- Causal forecasting and contradiction detection
- Strategic projection from world entities
- Temporal trend analysis

## APIs

- `GET /api/v1/runtime/world`
- `GET /api/v1/runtime/world/simulation`
- `POST /api/v1/runtime/world/project`
- `POST /api/v1/runtime/world/predict`
- `GET /api/v1/missions/{id}/simulation`

## Streaming

**Channels:** `world:runtime`, `simulation:runtime`

**Trace kinds:** `world_state_changed`, `simulation_projected`, `prediction_updated`

## Operator Console

`/runtime/world`, `/runtime/simulation`
