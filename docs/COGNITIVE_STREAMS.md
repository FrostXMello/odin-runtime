# Cognitive Streams

`core/cognitive_streams/` — continuous realtime cognition streams.

App handle: `app.cognitive_streams`

## Enable

```env
ODIN_COGNITIVE_STREAMS_ENABLED=1
```

## API

- `POST /api/v1/runtime/cognitive-streams/push`
- `POST /api/v1/runtime/cognitive-streams/reflect`

## Channel

`cognitive-streams:runtime`

Trace: `thought_stream_compressed`

Adaptive compression and low-resource fallback for GTX 1650 Ti / M-series MacBooks.
