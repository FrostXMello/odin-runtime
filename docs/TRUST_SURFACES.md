# Trust Surfaces

`core/trust_surfaces/` — operator trust and supervision integrity.

App handle: `app.trust_surfaces`

## Enable

```env
ODIN_TRUST_SURFACES_ENABLED=1
```

## API

- `GET /api/v1/runtime/trust-surfaces`
- `GET /api/v1/runtime/trust-surfaces/confidence`
- `GET /api/v1/runtime/supervision-integrity`

## Channel

`trust-surfaces:runtime`

## Trace kinds

- `operator_trust_updated`
- `supervision_integrity_evaluated`

Transparent, explainable, bounded, operator-visible trust scoring.
