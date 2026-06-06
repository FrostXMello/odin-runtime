# Safe Patching

Supervised patch pipeline with mandatory rollback plans.

## Rules

- No direct commits to main
- Approval required before merge
- Automatic branch isolation
- Sandbox application only
- Test impact analysis

## API

- `GET /api/v1/runtime/patches`
- `POST /api/v1/runtime/patches/plan`
- `POST /api/v1/runtime/patches/sandbox`

Trace kinds: `patch_generated`, `patch_validated`, `rollback_prepared` on `patches:runtime`.
