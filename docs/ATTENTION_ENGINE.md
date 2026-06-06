# Attention Engine

`core/attention_engine/` — salience scoring and focus routing.

App handle: `app.attention_engine`

Distinct from P51 `app.attention_flow`.

## Enable

```env
ODIN_ATTENTION_ENGINE_ENABLED=1
```

## API

- `POST /api/v1/runtime/attention/shift`
- `GET /api/v1/runtime/attention/heatmap`

## Channel

`attention:runtime`

Profiles: `survival`, `balanced`, `engineering`, `immersive`, `overnight`
