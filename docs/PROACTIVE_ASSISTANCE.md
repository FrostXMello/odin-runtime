# Proactive Assistance

`core/proactive_assistance/` — non-invasive contextual engineering hints.

App handle: `app.proactive_assistance_runtime`

Distinct from legacy `app.proactive` (ambient recommendations engine).

## Enable

```env
ODIN_PROACTIVE_ASSISTANCE_RUNTIME_ENABLED=1
```

## API

- `POST /api/v1/runtime/proactive-assistance/evaluate`

## Channel

`assistance:runtime`

Trace: `assistance_intervention_generated`

Operator-controlled, attention-safe, non-invasive.
