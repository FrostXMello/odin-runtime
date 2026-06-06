# Continuous Cognition

Bounded persistent cognition with adaptive throttling.

## Capabilities

- Cognitive tick engine with CPU/RAM budgets
- Deferred thought queues
- Background synthesis
- Continuity snapshots across restarts

## API

- `GET /api/v1/runtime/live-cognition`
- `POST /api/v1/runtime/live-cognition/tick`

Pauses during heavy load and on battery. Trace: `cognition_tick_completed` on `cognition:runtime`.
