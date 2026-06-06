# Operator Intelligence V2

`core/operator_intelligence_v2/` — transparent operator behavior modeling.

App handle: `app.operator_intelligence_v2`

Distinct from legacy `app.operator_intelligence` (research validation).

## Enable

```env
ODIN_OPERATOR_INTELLIGENCE_V2_ENABLED=1
```

## API

- `POST /api/v1/runtime/operator-intelligence-v2/analyze`

## Channel

`operator-intelligence:runtime`

Local-only. No manipulation framing. Operator-controlled recommendations.
