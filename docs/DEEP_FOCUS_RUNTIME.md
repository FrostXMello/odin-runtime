# Deep Focus Runtime

Deep work orchestration via `DeepFocusCoordinator` in operator intelligence V3.

## Enable

```env
ODIN_DEEP_FOCUS_ENABLED=1
ODIN_OPERATOR_INTELLIGENCE_V3_ENABLED=1
```

## API

- `POST /api/v1/runtime/deep-focus/start`

Trace: `deep_focus_session_started` → `productivity-v3:runtime`

Operator page: `/deep-focus`

Interruption minimization with operator-controlled session boundaries.
