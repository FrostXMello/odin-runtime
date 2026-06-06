# Conversational OS

`core/conversational_os/` — conversational operating layer.

## Capabilities

- Natural command routing (mission, benchmark, focus, debug, status, restore)
- Persistent conversational threads
- Workspace-context-aware dialogue
- Unified voice/text session metadata

Integrates with `conversation` runtime from P41.

## API

- `GET/POST /api/v1/runtime/conversational-os`
- `POST /api/v1/runtime/conversational-os/restore`

Channel: `conversational-os:runtime`
