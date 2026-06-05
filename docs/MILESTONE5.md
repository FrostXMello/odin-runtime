# Milestone 5 — Ambient Cognitive Operating Layer

## Backend modules

| Module | Path | Purpose |
|--------|------|---------|
| Context Engine | `context_engine/` | Situational awareness, snapshots, correlation |
| Desktop Semantics | `desktop_semantics/` | Window classification, workspace summaries |
| Execution Intelligence | `execution_intelligence/` | Tool reliability, strategy recommendations |
| Collaboration | `collaboration/` | Multi-agent chains via ODIN |
| Unified Cognitive Stream | `cognitive_stream/` | Aggregated multi-modal timeline |
| Memory Consolidation | `memory/consolidation/` | Dedup, patterns, relationship strengthening |
| Proactive Assistance | `proactive/` | Explainable, dismissible recommendations |
| Local Models | `local_models/` | Ollama lifecycle and scheduling |
| Policy Engine | `policies/` | Contextual Heimdall expansion |

## API highlights (`/api/v1`)

- `GET/PATCH /context-engine` — continuous context
- `GET /desktop-semantics/summary`
- `GET /cognitive-stream/timeline`
- `GET /proactive/recommendations`
- `GET /execution-intelligence/reliability`
- `GET /local-models/status`
- `GET /overlay/actions` — contextual command palette actions
- `GET /policies`

## Principles

- **Opt-in** desktop/context awareness
- **Recommendation-first** proactive assistance (no auto-execution)
- **Explainable** context and security decisions
- All collaboration routes through ODIN orchestration
- Policy engine runs before Heimdall on tool execution

## Tests

```powershell
cd odin\backend
$env:PYTHONPATH=".\"
.\.venv\Scripts\python -m pytest tests/test_milestone5.py -v
```
