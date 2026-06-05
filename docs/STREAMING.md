# Odin Real-Time Event Streaming

## Overview

Odin streams typed observability events over WebSockets while keeping all existing REST APIs as the source of truth and fallback. The stack is **local-first**: an in-process `StreamingEventBus` fans out to per-channel subscriber queues; no Redis or Kafka required.

## Architecture

```
Tracer / Lifecycle / Heartbeat
        ↓
   StreamBridge (publish_nowait)
        ↓
   StreamingEventBus (async fan-out)
        ↓
   WebSocketManager (per-connection pump)
        ↓
   Operator Console (useRealtimeChannel → React Query cache)
```

### Backend (`core/streaming/`)

| Module | Role |
|--------|------|
| `event_bus.py` | Global async pub/sub, channel queues, stats |
| `serializers.py` | `StreamEnvelope`, `StreamEventKind`, trace→stream mapping |
| `subscriptions.py` | Channel specs and matching rules |
| `websocket_manager.py` | Accept, replay, pump, ping/pong |
| `heartbeat.py` | Periodic `heartbeat`, `health_changed`, `bottleneck_detected` |
| `bridge.py` | Hooks tracer + mission lifecycle into the bus |

### WebSocket endpoints

| Path | Channel |
|------|---------|
| `GET /api/v1/ws/runtime` | `runtime` (all events) |
| `GET /api/v1/ws/missions/{id}` | `mission:{id}` + replay |
| `GET /api/v1/ws/tasks/{id}` | `task:{id}` + replay |
| `GET /api/v1/ws/traces/{id}` | `trace:{id}` + replay |
| `GET /api/v1/ws/stats` | Bus metrics (HTTP) |

### Event kinds

`mission_created`, `mission_state_changed`, `task_started`, `task_completed`, `task_failed`, `retry_triggered`, `escalation_triggered`, `signal_propagated`, `memory_mutated`, `health_changed`, `bottleneck_detected`, `heartbeat`, `connected`, …

## Frontend (Operator Console)

- `hooks/useRealtimeChannel.ts` — connect, reconnect, stale detection, metrics
- `hooks/useRuntimeStream.ts` — global runtime feed
- `hooks/useMissionStream.ts` — mission / task / trace channels
- `lib/stream/cache-updates.ts` — patches TanStack Query cache from envelopes
- UI: LIVE badge, connection health, activity ticker, graph node flash, slower REST polling when stream is up

Set `NEXT_PUBLIC_WS_BASE=ws://127.0.0.1:8000/api/v1/ws` (Next.js does not proxy WebSockets through rewrites).

## Demo flow

1. Start backend: `uvicorn odin_backend.api.main:app` (port 8000).
2. Start operator: `cd odin/operator && npm run dev` (port 3000).
3. Open `/runtime` — sidebar shows **LIVE** when WS connects; activity ticker shows events.
4. Create or run a mission — timeline entries appear without full page refresh.
5. Open `/graph` — signal events flash affected nodes.
6. Disable network briefly — badge shows **reconnecting**; REST polling continues at 4× interval.

## Scaling limitations

- Single-process memory queues (max 512 events per subscriber; drops counted in stats).
- No cross-node fan-out; horizontal scaling needs a shared pub/sub layer.
- `runtime` subscribers receive all events (by design for the ops dashboard).

## Future upgrade path

1. Replace `StreamingEventBus` backend with Redis Pub/Sub or NATS while keeping `StreamEnvelope` and WS routes unchanged.
2. Add SSE fallback for environments that block WebSockets.
3. Optional event persistence / replay window in object storage for multi-hour audits.
4. Auth-scoped channels per tenant when multi-user deployments ship.
