# Cognitive Planning

`core/cognitive_planning/` — adaptive cognitive planning and reasoning budgets.

App handle: `app.cognitive_planning`

## Enable

```env
ODIN_COGNITIVE_PLANNING_ENABLED=1
ODIN_REASONING_BUDGET_MODE=adaptive
```

Modes: `compact`, `balanced`, `engineering`, `immersive`, `overnight_autonomous`.

## API

- `POST /api/v1/runtime/cognitive-planning/generate`
- `GET /api/v1/runtime/cognitive-planning/budget`

## Channel

`cognitive-planning:runtime`

## Trace kinds

- `cognitive_plan_generated`
- `reasoning_budget_rebalanced`

Adaptive reasoning throttling. Low-power planning. No autonomous deployment.
