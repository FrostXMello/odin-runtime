# Desktop Attention

`core/desktop_attention/` — desktop-level attention routing and salience scoring.

App handle: `app.desktop_attention`

## Enable

```env
ODIN_DESKTOP_ATTENTION_ENABLED=1
```

## API

- `GET /api/v1/runtime/desktop-attention`
- `POST /api/v1/runtime/desktop-attention/salience`

## Channel

`desktop-attention:runtime`

## Trace kinds

- `desktop_attention_rebalanced`
- `workspace_salience_updated`

Integrates with `attention_engine`, `live_overlays_v2`.

Bounded cognition. Low-priority surface suppression. Stream prioritization for constrained hardware (GTX 1650 Ti, 16GB RAM, M-series MacBook).
