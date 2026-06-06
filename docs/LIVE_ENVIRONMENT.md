# Live Environment

`core/live_environment/` — adaptive personal operating layer.

## Capabilities

- Operator presence tracking
- Focus vs distraction detection
- Interruption classification
- Environmental context (battery, heavy load)
- Adaptive cognition intensity

## Constraints

- Local-only
- Privacy-preserving
- Bounded cognition

## API

- `POST /api/v1/runtime/live-environment/update`

Channel: `live-environment:runtime`

Traces: `focus_state_changed`, `interruption_classified`, `adaptive_presence_updated`
