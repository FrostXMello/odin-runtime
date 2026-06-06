# Continuous Reasoning

Bounded continuous reasoning via `RealtimeCognitionRuntime` and `ContinuousReasoningRuntime`.

## Enable

```env
ODIN_CONTINUOUS_REASONING_ENABLED=1
ODIN_REALTIME_COGNITION_ENABLED=1
```

## API

- `POST /api/v1/runtime/realtime-cognition/reason`
- `GET /api/v1/runtime/continuous-reasoning`

Trace: `continuous_reasoning_updated` → `realtime-cognition:runtime`

Operator page: `/continuous-reasoning`

Frontend: `DesktopV3Panels.tsx` — `ContinuousReasoningOverlay`, `RealtimeCognitionRiver`
