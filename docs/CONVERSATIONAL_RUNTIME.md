# Conversational Runtime

Real-time conversational cognition in `core/conversation_runtime/`.

## Modes

`assistant`, `engineering`, `research`, `strategic`, `debugging`, `copilot`, `reflective`

## Features

- Token streaming responses
- Live reasoning visualization chunks
- Interruption recovery
- Conversation memory threads with session restore
- Adaptive tone per mode

## API

- `GET /api/v1/runtime/conversation`
- `POST /api/v1/runtime/conversation`
- `POST /api/v1/runtime/conversation/restore`

## Traces

- `thought_generated`
- `conversation_thread_restored`

Channel: `conversation:runtime`

## Voice integration

Extended `core/realtime_voice/` with emotional TTS metadata, transcription overlay, adaptive profiles, and low-latency streaming config.
