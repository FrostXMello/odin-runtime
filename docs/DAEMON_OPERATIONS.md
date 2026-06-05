# Daemon Operations (v0.35)

Extended daemon mode for week-long uptime with bounded RAM.

## Capabilities

- Persistent heartbeat tracking
- Idle sleep scheduling and wake-on-activity
- Session restore after crash (`daemon_restored`)
- Memory compaction during idle
- Adaptive polling intervals

## APIs

- `GET /api/v1/runtime/daemon`
- `POST /api/v1/runtime/daemon/start`
- `POST /api/v1/runtime/daemon/restore`
