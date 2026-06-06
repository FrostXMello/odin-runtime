# Conversational Presence

`core/conversational_presence/` — persistent conversational operating layer.

## Modules

- `presence_runtime.py` — `ConversationalPresenceRuntime`
- `presence_sessions.py` — session threads
- `realtime_turn_manager.py` — turn sequencing
- `interrupt_reasoning.py` — interruption handling
- `conversation_memory_threads.py` — contextual recall
- `voice_attention.py` / `emotion_signals.py` — cadence + emotion metadata
- `conversation_continuity.py` — thread restoration

## Enable

```env
ODIN_CONVERSATIONAL_PRESENCE_ENABLED=1
ODIN_REALTIME_VOICE_ENABLED=1
```

## API

- `POST /api/v1/runtime/conversational-presence/connect`
- `POST /api/v1/runtime/conversational-presence/turn`
- `POST /api/v1/runtime/conversational-presence/interrupt`

## Channel

`presence-live:runtime`

## Traces

`live_presence_updated`, `conversation_memory_recalled`

Voice remains local-first, bounded, and supervision-compatible.
