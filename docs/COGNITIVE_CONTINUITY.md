# Cognitive Continuity

Long-horizon memory threads and session restore.

## Capabilities

- Active memory threads per project
- Unfinished work tracking
- Cognitive session restore
- Continuity linking across restarts

## API

- `GET /api/v1/runtime/continuity`
- `POST /api/v1/runtime/continuity/restore`
- `POST /api/v1/runtime/continuity/track`

Trace kinds: `unfinished_work_detected`, `continuity_restored_live` on `continuity:runtime`.
