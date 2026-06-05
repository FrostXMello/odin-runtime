# Milestone 4 — Conversational Cognitive OS

## Backend

| Module | Path | Purpose |
|--------|------|---------|
| Conversation | `conversation/` | Sessions, continuity, compression, objectives |
| Knowledge graph | `knowledge_graph/` | NetworkX entity graph, traversal, search |
| Sandbox | `sandbox/` | Execution profiles, snapshots, Heimdall scope |
| Vision | `vision/` | Screenshot/OCR/UI interpretation (no auto-click) |
| Personalization | `personalization/` | Behavioral profiles, preference learning |
| Reflection | `reflection/` | Post-workflow analysis and recommendations |
| Persistent workflows | `workflows/persistent.py` | Pause/resume/cancel/checkpoints |
| Voice streaming | `voice/streaming/` | Progressive STT/TTS with interruption |
| AI routing | `ai/routing/intelligent_router.py` | Local/cloud selection |

## API (`/api/v1`)

- `POST /conversation/chat` — full turn: continuity → plan → execute → reflect
- `GET/POST /conversation/sessions`
- `GET /knowledge-graph/search`, `/project/{id}/dependencies`
- `POST /sandbox/execute`
- `GET/POST /persistent-workflows`
- `GET /reflection/{workflow_id}`
- `GET /personalization/profile`

## Frontend

- **Alt+Space** overlay command palette (`?mode=overlay`)
- Panels: Conversation, Knowledge Graph, Reflection, Voice, Sandbox, Objectives

## Principles

- ODIN plans; agents execute; Heimdall enforces
- All workflows traceable; long-running workflows reversible
- No uncontrolled autonomy or hidden execution

## Tests

```powershell
cd odin\backend
$env:PYTHONPATH=".\"
.\.venv\Scripts\python -m pytest tests/test_milestone4.py -v
```
