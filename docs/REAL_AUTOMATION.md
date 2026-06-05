# Real Automation (v0.35)

Verified desktop automation with approval-safe execution modes.

## Modes

- `simulation` — default, no real I/O
- `supervised` — routes through action approval
- `semi-autonomous` — verified execution with retry paths

## Modules

- `core/automation/automation_runtime.py` — orchestrator (`app.automation_runtime`)
- `core/automation/action_verification.py` — OCR/DOM/click confidence checks

## Configuration

```env
ODIN_REAL_AUTOMATION_ENABLED=true
ODIN_AUTOMATION_MODE=simulation
```

## API

- `GET /api/v1/runtime/automation-live`
- `POST /api/v1/runtime/automation-live/execute`
