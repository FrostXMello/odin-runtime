# Stream Management

`core/stream_management/` — stream compression, prioritization, and stale channel pruning.

App handle: `app.stream_management`

## Enable

```env
ODIN_STREAM_MANAGEMENT_ENABLED=1
ODIN_STREAM_COMPRESSION_MODE=adaptive
```

## API

- `POST /api/v1/runtime/stream-management/compress`
- `POST /api/v1/runtime/stream-management/prune`

## Channel

`stream-management:runtime`

## Trace kinds

- `stream_channels_compressed`
- `stale_streams_pruned`

Bounded batch size (64). Adaptive stream batching and density stabilization.
