# Evolution Review

`core/evolution_review/` — visual supervised self-development workflow.

## Modules

- `review_runtime.py` — `EvolutionReviewRuntime` (`app.evolution_review`)
- `proposal_queue.py` — pending upgrades
- `upgrade_visualizer.py` — visual proposal graph
- `benchmark_diffs.py` / `regression_compare.py` — drift analysis
- `approval_workflows.py` — approve / reject / revise (no auto-commit)
- `rollback_explorer.py` — rollback simulation
- `patch_timeline.py` — architecture history

## Enable

```env
ODIN_EVOLUTION_REVIEW_ENABLED=1
ODIN_EVOLUTION_APPROVAL_LEVEL=proposal_only
```

## API

- `POST /api/v1/runtime/evolution-review/open`
- `POST /api/v1/runtime/evolution-review/rollback`
- `POST /api/v1/runtime/evolution-review/decide`

## Channel

`evolution-review:runtime`

## Traces

`upgrade_review_opened`, `rollback_simulated`

**No automatic source modification. No direct commits to main.**
