# Autonomous Patching

`core/autonomous_patching/` — isolated branch patch pipeline.

## Flow

1. Plan patch on isolated branch (`odin-evolve-*`)
2. Validate diff in sandbox
3. Run local benchmarks
4. Detect regression → mandatory rollback plan
5. Merge recommendation (always approval-required)

Integrates with existing `safe_patching` and `validation_fabric`.

## API

- `GET /api/v1/runtime/patch-pipeline`
- `POST /api/v1/runtime/patch-pipeline/run`
- `POST /api/v1/runtime/patch-pipeline/rollback`

## Constraints

- **No commits to main/master**
- Rollback plan mandatory
- Internet patch ingestion disabled
