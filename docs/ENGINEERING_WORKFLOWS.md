# Engineering Workflows

Development lifecycle orchestration.

## Capabilities

- Goal → task breakdown
- Implementation sequencing
- Issue tracking and blocked work detection
- Sprint memory and retrospectives
- Milestone tracking

## API

- `GET /api/v1/runtime/workflows`
- `POST /api/v1/runtime/workflows/goal`
- `GET /api/v1/runtime/engineering/briefing`

Trace kinds: `engineering_goal_created`, `implementation_blocked` on `engineering:runtime`.
