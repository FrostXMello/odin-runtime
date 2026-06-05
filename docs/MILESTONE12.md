# Milestone 12 — Execution Reality + VALKYRIE + Environment Control

## Objective

Controlled real-world execution via environment-driven config, execution gate, and VALKYRIE dispatch.

## Components

| Path | Role |
|------|------|
| `environment_control/` | `OdinEnvironmentConfig` — all runtime flags from `.env` |
| `agents/valkyrie/engine.py` | `ValkyrieExecutionEngine` — governed real execution |
| `core/execution_gate/` | Final safety: ALLOW / BLOCK / ESCALATE / REQUIRE_CONFIRMATION |
| `tools/execution/executors.py` | FS, OS, browser, clipboard executors |
| `tools/execution/pipeline.py` | Full trace: governor + gate + Heimdall + memory event |

## Execution pipeline

```
Signal → Kernel → Priority → Coherence → Governor → ExecutionGate → VALKYRIE → Tool → Memory → Graph → Stability
```

## Environment (`.env`)

See `odin/.env` and `odin/backend/.env.example`.

Key flags:
- `ODIN_VALKYRIE_ENABLED=false` (safe default)
- `ODIN_DESKTOP_CONTROL_ENABLED=false`
- `ODIN_AUTONOMY_LEVEL=1`

## API

- `GET /api/v1/valkyrie/status`
- `POST /api/v1/valkyrie/execute`
- `POST /api/v1/valkyrie/chain`

## Safety

- No OS/desktop mutation without `ODIN_VALKYRIE_ENABLED` + `ODIN_DESKTOP_CONTROL_ENABLED`
- High-risk tools require `user_confirmed`
- Kernel reads behavior from `OdinEnvironmentConfig` only

## Tests

```powershell
pytest tests/test_milestone12.py -v
```
