# Operator Veto

`core/operator_veto/` — operator intervention gates and recovery approval routing.

App handle: `app.operator_veto`

All recovery execution must route through this runtime.

## Enable

```env
ODIN_OPERATOR_VETO_ENABLED=1
```

## API

- `POST /api/v1/runtime/operator-veto/request`
- `POST /api/v1/runtime/operator-veto/authorize`
- `POST /api/v1/runtime/operator-veto/veto`
- `GET /api/v1/runtime/operator-veto`
- `GET /api/v1/runtime/recovery-authorization`

## Channel

`operator-veto:runtime`

## Trace kinds

- `operator_veto_requested`
- `recovery_chain_authorized`
- `recovery_path_vetoed`

Trust-preserving escalation. Transparent intervention. No hidden rollback execution.
