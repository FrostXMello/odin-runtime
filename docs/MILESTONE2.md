# Milestone 2 — Intelligence + Execution Layer

## New Systems

### Reasoning (`orchestrator/reasoning/`)
- `ReasoningEngine` — objectives → structured `WorkflowPlan`
- `Planner` — OpenAI JSON planning with rule-based fallback
- `WorkflowBuilder`, `ToolSelector`, `PromptManager`

### AI Providers (`ai/`)
- `OpenAIProvider` — async, retries, JSON mode
- `ModelRouter` — swappable backends

### MIMIR Memory (`memory/`)
- **Episodic** — workflow/action history
- **Structured** — SQLite preferences, workflow logs, agent states
- **Semantic** — ChromaDB with in-memory fallback
- `MimirCoordinator` — single entry point (`save_memory`, `search_memory`)

### Tool Runtime (`tools/runtime/`)
- Tracing, timeouts, retries, audit logging
- All execution via `HeimdallService`

### Real Tools (`tools/implementations/`)
- Filesystem, web search, terminal (sandboxed), browser (Playwright), content, email

### Workflow Runner (`workflows/runner.py`)
- Sequential plan execution: LLM → plan → steps → tools

### Observability
- `TraceManager`, `AuditLogger`, `EventHub`
- SSE: `GET /api/v1/events/stream`

### HEIMDALL (`permissions/heimdall.py`)
- Permission interception, pending approvals, audit

## API

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/objectives` | Reason + execute workflow |
| `GET /api/v1/workflows` | List workflow runs |
| `GET /api/v1/events/stream` | SSE live events |
| `POST /api/v1/memory/search` | Semantic search |
| `GET /api/v1/permissions/pending` | Pending approvals |
| `GET /api/v1/observability/traces` | Execution traces |

## Configuration

Set `ODIN_OPENAI_API_KEY` for LLM planning. Without it, rule-based planning is used.

Optional: `playwright install chromium` for browser tools.
