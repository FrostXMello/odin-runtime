# Live Reasoning

Streaming reasoning visualization via `core/cognitive_visualization/`.

## Capabilities

- Live reasoning graph (`cognition_graph`, `live_reasoning_map`)
- Thought stream pipeline (`thought_stream`)
- Execution flow and memory activity maps
- Agent activity and strategy visualizers
- Runtime load heatmaps

## API

- `GET /api/v1/runtime/cognition-live`
- `GET /api/v1/runtime/thought-stream`
- `POST /api/v1/runtime/thought-stream/push`
- `GET /api/v1/runtime/reasoning-map`

## Streaming

Trace kinds: `thought_generated`, `reasoning_stream_updated`

Channels: `cognition-live:runtime`, `thought-stream:runtime`

## Resource modes

Adaptive framerate via `cognitive_interface_mode` — throttles GPU/UI in `minimal` and `balanced` modes.
