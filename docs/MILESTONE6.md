# Milestone 6 — Persistent AI Operating Environment

## Backend

| Module | Path | Purpose |
|--------|------|---------|
| Desktop Runtime | `desktop_runtime/` | Live context ingestion, explainable collectors |
| Workspace Intelligence | `workspace_intelligence/` | Session classification, project tracking |
| Live Cognition | `live_cognition/` | Attention system, operational state |
| Resilience | `resilience/` | Circuit breakers, workflow recovery |
| Agent Society | `agent_society/` | Capabilities, reputation, routing |
| Preference Evolution | `personalization/evolution.py` | Transparent adaptation |
| Memory Evolution | `memory/evolution/` | Longitudinal timelines, summaries |
| Compute | `compute/` | Local-first scheduling, embeddings |
| Security Trust | `security/trust.py` | Trust scores, escalation |
| Workspace Automation | `workspace_automation/` | Contextual actions |

## Electron

- `electron/context_bridge/` — opt-in collector posting to `/desktop-runtime/ingest`

## API

- `GET/PATCH /desktop-runtime`
- `POST /desktop-runtime/ingest`
- `GET /workspace-intelligence/summary`
- `GET /live-cognition/state`
- `GET /resilience/status`
- `GET /agent-society`
- `GET /compute/dashboard`
- `GET /workspace-automation/actions`
- `GET /trust/dashboard`

## Principles

- Opt-in desktop collection with explainable sources
- ODIN remains supreme orchestrator
- Failures degrade gracefully with recovery reports
- All automation suggestions require approval

## Tests

```powershell
cd odin\backend
$env:PYTHONPATH=".\"
.\.venv\Scripts\python -m pytest tests/test_milestone6.py -v
```
