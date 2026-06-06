# Collaborative Cognition

`core/collaborative_cognition/` — multi-operator cognition orchestration and synchronized shared attention.

App handle: `app.collaborative_cognition`

## Enable

```env
ODIN_COLLABORATIVE_COGNITION_ENABLED=1
ODIN_COLLABORATION_PROFILE=balanced
```

## Profiles

`solo`, `pair`, `team`, `supervisory`, `overnight_collaboration`

## API

- `GET /api/v1/runtime/collaborative-cognition/state`
- `POST /api/v1/runtime/collaborative-cognition/synchronize`
- `POST /api/v1/runtime/collaborative-cognition/initialize`

## Channel

`collaborative-cognition:runtime`

## Trace kinds

- `collaborative_cognition_initialized`

Integrates with `operator_sessions`, `team_coordination`, and shared command surfaces. Bounded synchronization loops (max 48). Transparent, permission-aware, operator-visible.
