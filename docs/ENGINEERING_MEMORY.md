# Engineering Memory

Odin v0.39 persists long-term engineering context across sessions.

## Stores

- Repository structure over time
- Architectural decisions
- Bug/fix history and failed fixes
- Patch outcomes
- Engineering sessions and timelines
- Dependency evolution

## API

- `GET /api/v1/runtime/engineering`
- `POST /api/v1/runtime/engineering/record-repo`
- `POST /api/v1/runtime/engineering/record-bug`

Trace: `repository_graph_updated` on `engineering:runtime` and `repositories:runtime`.
