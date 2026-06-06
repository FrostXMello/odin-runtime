# Cognitive Daemon

Extended `core/daemon/` with persistent cognitive presence.

## New modules

- `persistent_presence`, `cognition_scheduler`, `wake_intelligence`
- `deferred_reasoning`, `realtime_attention`, `operator_interrupts`

## Capabilities

- Bounded background cognition ticks
- Wakeword-triggered attention (local-only)
- Deferred reasoning queue
- Interruption recovery
- Overnight survival mode throttling

## Enable

```env
ODIN_DAEMON_MODE_ENABLED=1
ODIN_COGNITIVE_DAEMON_ENABLED=1
```

## API

- `GET /api/v1/runtime/cognitive-daemon`
- `POST /api/v1/runtime/cognitive-daemon/tick`

Traces: `daemon_attention_shifted`, `persistent_presence_updated`, `operator_interrupt_received`

Channel: `daemon:runtime`
