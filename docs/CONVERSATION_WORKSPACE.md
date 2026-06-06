# Conversation Workspace

`core/conversation_workspace/` — unified chat + cognitive stream orchestrator.

## Panels

Chat · thought stream · reasoning graph · missions · agents · workspace context · memory threads.

## Enable

```env
ODIN_CONVERSATION_WORKSPACE_ENABLED=1
```

## API

- `POST /api/v1/runtime/conversation-workspace/open`
- `POST /api/v1/runtime/conversation-workspace/interact`

App handle: `app.conversation_workspace`

## Features

- Streaming responses via `conversational_os` + `reasoning_streams`
- Inline approvals (supervised)
- Mission spawning from chat
- Persistent conversation restore via `persistent_cognition`

## Traces

`conversation_workspace_opened`, `live_reasoning_rendered` → `workspace-ui:runtime`
