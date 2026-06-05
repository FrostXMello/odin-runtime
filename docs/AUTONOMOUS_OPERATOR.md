# Autonomous Operator Mode (v0.27)

Odin can run as a continuously operating local cognitive system under operator-supervised policy constraints.

## Architecture

```
core/autonomy/     Autonomous loop, objectives, scheduler, initiative engine
core/environment/  Local runtime/resource/topology monitoring
core/research/     Iterative local research sessions with agent debate
core/identity/     Persistent bounded personality state
core/safety/       Throttles, loop detection, permission modes
```

## Permission modes

| Mode | Behavior |
|------|----------|
| `observe_only` | Monitor only, no mission spawn |
| `supervised` | Default — objectives tracked, missions require approval |
| `semi_autonomous` | Limited proactive missions |
| `research_only` | Research loops only |
| `fully_local_autonomous` | Local bounded autonomy with throttles |

## Configuration

```env
ODIN_AUTONOMOUS_OPERATOR_ENABLED=false
ODIN_AUTONOMY_MODE=supervised
ODIN_AUTONOMY_CYCLE_INTERVAL_SECONDS=60
ODIN_AUTONOMY_MISSION_BUDGET_PER_HOUR=5
```

## APIs

| Method | Path |
|--------|------|
| GET/POST | `/api/v1/runtime/autonomy` |
| POST | `/api/v1/runtime/autonomy/start` |
| POST | `/api/v1/runtime/autonomy/pause` |
| GET/POST | `/api/v1/runtime/objectives` |
| GET/POST | `/api/v1/runtime/research/start` |
| GET/PATCH | `/api/v1/runtime/identity` |
| GET | `/api/v1/runtime/environment` |
| GET | `/api/v1/runtime/safety` |

## Safety guarantees

- No unrestricted self-modifying code
- Mission generation throttled per hour
- Runaway loop detection
- Reflection/recursion depth caps (from Prompt 26)
- Identity updates bounded to ±0.15 per trait per edit
- Autonomous operator **disabled by default**

## Operator Console

- `/runtime/autonomy` — start/pause, loop metrics
- `/runtime/objectives` — persistent goal graph
- `/runtime/research` — research sessions
- `/runtime/identity` — behavioral profile
- `/runtime/environment` — local alerts
- `/runtime/safety` — interventions and throttles
