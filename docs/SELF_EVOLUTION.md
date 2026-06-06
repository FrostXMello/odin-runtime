# Self-Evolution Loop

Prompt 42 supervised self-development engineering cycles.

## Orchestrator

`core/self_evolution/` — `SelfEvolutionRuntime` (`app.self_evolution`)

Bounded cycle: observe → analyze → propose → simulate → validate → request approval → branch apply → benchmark → rollback check → learn

Guards: recursion depth ≤ 3, 60s cooldown, no main commits.

## Enable

```env
ODIN_SELF_EVOLUTION_ENABLED=1
ODIN_SELF_IMPROVEMENT_MEMORY_ENABLED=1
ODIN_AUTONOMOUS_PATCHING_LOOP_ENABLED=1
ODIN_RUNTIME_BENCHMARKS_ENABLED=1
ODIN_EVOLUTION_GOVERNANCE_ENABLED=1
ODIN_SELF_OPTIMIZING_ROUTING_ENABLED=1
ODIN_EVOLUTION_APPROVAL_LEVEL=proposal_only
ODIN_SELF_EVOLUTION_MODE=balanced
```

Approval levels: `observe_only`, `proposal_only`, `supervised_apply`, `supervised_merge`
