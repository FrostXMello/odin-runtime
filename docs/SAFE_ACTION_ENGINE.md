# Safe Action Engine (Prompt 29)

Odin Runtime extends multimodal operator intelligence with a supervised action engine for desktop automation, browser control, workflow macros, and human-in-the-loop execution.

## Enable

```env
action_engine_enabled=true
desktop_automation_enabled=true
browser_operator_enabled=true
automation_simulation_mode=true
approval_mode=manual_every_step
overlay_enabled=true
```

**Default:** `action_engine_enabled=false`, `automation_simulation_mode=true` (no real mouse/keyboard until explicitly disabled).

## Architecture

| Layer | Path | App attribute |
|-------|------|---------------|
| Actions | `core/actions/` | `action_runtime`, `action_scheduler` |
| Automation | `core/automation/` | `automation_sandbox` |
| Browser | `core/browser_operator/` | `browser_operator` |
| Supervision | `core/supervision/` | `supervision_runtime` |
| Macros | `core/workflow_macros/` | `macro_replay`, `workflow_memory` |
| Safety | `core/action_safety/` | `action_safety` |
| Overlay | `core/overlay/` | `overlay_runtime` |

## Action lifecycle

`proposed` → `awaiting_approval` → `approved` → `executing` → `completed`

Blocked/destructive actions never execute. Emergency stop pauses all in-flight automation.

## APIs

- `GET /api/v1/runtime/actions`
- `POST /api/v1/runtime/actions/propose`
- `POST /api/v1/runtime/actions/{id}/approve|pause|cancel|revert`
- `GET /api/v1/runtime/workflows`
- `POST /api/v1/runtime/workflows/record/start|stop`
- `GET /api/v1/runtime/browser`
- `POST /api/v1/runtime/browser/session/start`
- `GET /api/v1/runtime/supervision`
- `POST /api/v1/runtime/emergency-stop`
- `GET /api/v1/runtime/automation`
- `GET /api/v1/runtime/overlay`

## Safety

- Risk classification: `safe`, `supervised`, `restricted`, `blocked`
- Destructive actions blocked (delete, shell escalation, credential harvest)
- Sensitive data detection in payloads
- Protected app restrictions (password managers, banking)
- Rate-limited automation with emergency stop
- Simulation mode by default

## Operator Console

`/runtime/actions`, `/automation`, `/browser`, `/workflows`, `/supervision`, `/overlay`

## Streaming channels

`actions:runtime`, `automation:runtime`, `browser:runtime`, `workflows:runtime`, `supervision:runtime`
