# Persistent Cognition

`core/persistent_cognition/` — SQLite-backed cognition state persistence.

## Capabilities

- Continuity checkpoints
- Session rehydration after restart
- Deferred intentions
- Long-running thread restoration
- Daemon snapshot integration

## Enable

```env
ODIN_PERSISTENT_COGNITION_ENABLED=1
```

## API

- `POST /api/v1/runtime/persistent-cognition/checkpoint`
- `POST /api/v1/runtime/persistent-cognition/rehydrate`

Traces: `cognition_checkpoint_created`, `session_rehydrated` → `cognition:continuity`
