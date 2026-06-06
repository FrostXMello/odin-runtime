# Operator Alignment

`core/operator_alignment/` — bounded adaptive assistance alignment.

App handle: `app.operator_alignment`

## Enable

```env
ODIN_OPERATOR_ALIGNMENT_ENABLED=1
```

## API

- `GET /api/v1/runtime/operator-alignment`
- `POST /api/v1/runtime/operator-alignment/adapt`
- `GET /api/v1/runtime/supervision-confidence`

## Channel

`operator-alignment:runtime`

## Trace kinds

- `operator_alignment_updated`

Integrates with `operator_intelligence_v4`, `personal_presence`, `desktop_attention`, `operator_focus`.

Bounded adaptive behavior. Operator override required. Transparent drift detection.
