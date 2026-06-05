# PROJECT ODIN

Production-grade personal autonomous AI operating system — orchestrator, agents, memory, tools, and desktop command center.

## Stack

| Layer          | Technology                          |
|----------------|-------------------------------------|
| Frontend       | Electron, React, Tailwind, Zustand  |
| Backend        | Python, FastAPI, Pydantic, AsyncIO  |
| Events / Queue | Redis Pub/Sub + sorted sets           |
| Memory         | In-memory foundation → ChromaDB     |

## Quick Start

### 1. Redis

```powershell
.\scripts\start-redis.ps1
```

Or: `docker compose -f infrastructure/docker/docker-compose.yml up -d`

### 2. Backend

```powershell
.\scripts\start-backend.ps1
```

API: http://127.0.0.1:8000/docs

### 3. Frontend

```powershell
.\scripts\start-frontend.ps1
```

## Project Structure

```
odin/
├── frontend/          # Electron + React
├── backend/           # FastAPI + orchestrator
├── infrastructure/    # Docker, Redis, DB
├── docs/              # Architecture docs
└── scripts/           # Dev scripts
```

## API Endpoints

| Method | Path                    | Description        |
|--------|-------------------------|--------------------|
| GET    | /api/v1/health          | Health check       |
| GET    | /api/v1/status          | System status      |
| POST   | /api/v1/objectives      | Reason + run workflow |
| POST   | /api/v1/tasks           | Submit task        |
| GET    | /api/v1/workflows       | Workflow runs      |
| GET    | /api/v1/events/stream   | SSE event stream   |
| GET    | /api/v1/agents          | List agents        |
| GET    | /api/v1/tools           | List tools         |
| POST   | /api/v1/memory/search   | Semantic search    |

See `docs/MILESTONE2.md` and `docs/MILESTONE3.md` for architecture details.

### Milestone 3 highlights
- Persistent runtime supervisor + heartbeats + recovery
- Background watchers (HUGIN, FAFNIR, HEIMDALL) — monitor only
- Chrome CDP browser intelligence
- Parallel/hybrid DAG workflow execution
- Live cognition streaming
- Advanced MIMIR (scoring, project clusters, summarization)
- Voice foundation (push-to-talk, optional)
- Opt-in desktop context awareness

## Development Principles

1. ODIN plans and delegates — agents execute
2. All communication is event-driven
3. Tools are modular, never hardcoded in agents
4. Permissions enforced on every tool invocation
5. Human override always available

## License

Private — PROJECT ODIN
