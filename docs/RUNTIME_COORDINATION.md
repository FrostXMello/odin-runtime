# Runtime Coordination

`core/runtime_coordination/` — synchronize runtime states and resolve conflicts.

App handle: `app.runtime_coordination`

## Enable

```env
ODIN_RUNTIME_COORDINATION_ENABLED=1
```

## API

- `GET /api/v1/runtime/runtime-coordination/conflicts`
- `POST /api/v1/runtime/runtime-coordination/resolve`

## Channel

`runtime-coordination:runtime`

Prevents duplicate cognition and merges overlapping objectives.
