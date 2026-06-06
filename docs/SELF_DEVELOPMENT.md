# Self-Development Supervision

Supervised self-improvement in `core/self_development/`.

## Constraints

Odin **must not** directly rewrite itself. It may only:

- Identify capability gaps
- Propose improvements
- Generate supervised patch plans
- Simulate upgrades

All code modification workflows require **human approval**.

## Modules

- `capability_gap_detector`
- `learning_opportunity_engine`
- `architecture_reflection`
- `supervised_evolution` — always returns `direct_modification: false`
- `improvement_queue`, `patch_proposal_pipeline`

## API

- `GET /api/v1/runtime/self-development`
- `POST /api/v1/runtime/self-development/analyze`
- `POST /api/v1/runtime/self-development/propose`

## Traces

- `improvement_proposed`
- `architecture_reflection_generated`

Channel: `self-development:runtime`
