# Delegation Engine

`core/delegation_engine/` — supervised task delegation and bounded authority routing.

App handle: `app.delegation_engine`

## Enable

```env
ODIN_DELEGATION_ENGINE_ENABLED=1
```

## API

- `POST /api/v1/runtime/delegation-engine/delegate`
- `POST /api/v1/runtime/delegation-engine/revoke`
- `GET /api/v1/runtime/delegation-engine`

## Channel

`delegation-engine:runtime`

## Trace kinds

- `delegation_chain_created`
- `delegation_authority_validated`

Delegation is approval-aware, reversible, and permission-aware. Replay loops are bounded and lazily hydrated.
