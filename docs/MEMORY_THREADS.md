# Memory Threads

`core/memory_threads/` — persistent semantic memory threads.

## Capabilities

- Cross-session context continuity
- Project and conversational threads
- Thread linking and prioritization
- Bounded decay (max 64 threads)

## API

- `POST /api/v1/runtime/memory-threads/activate`
- `GET /api/v1/runtime/memory-threads`

Channel: `memory-threads:runtime`

Trace: `memory_thread_activated`
