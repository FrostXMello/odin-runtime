# Knowledge Fabric + Internet Research (Prompt 30)

Odin Runtime extends local-first autonomous research and structured knowledge acquisition.

## Enable

```env
knowledge_fabric_enabled=true
research_fabric_enabled=true
web_access_enabled=false
web_access_allowlist=example.com,docs.local
research_budget_per_hour=10
web_rate_limit_per_minute=20
```

Default: all disabled. Web access uses read-only stubs until explicitly enabled.

## Architecture

| Layer | Path | App attribute |
|-------|------|---------------|
| Knowledge | `core/knowledge/` | `knowledge_runtime` |
| Research fabric | `core/research_engine/` | `research_fabric` |
| Web access | `core/web_access/` | `web_access` |
| Research agents | `core/research_agents/` | `research_agents` |
| World reasoning | `core/reasoning/` | `reasoning_world` |
| Governance | `core/knowledge/research_governance.py` | `research_governance` |

**Note:** `app.research_engine` (debate loop in `core/research/`) is preserved. Web research fabric is `app.research_fabric`.

## Knowledge item schema

Each node stores: id, entity, fact, confidence, source, timestamp, supporting/contradicting evidence, mission origin, reasoning chain.

SQLite tables: `odin_knowledge_nodes`, `odin_knowledge_relationships`, `odin_knowledge_sources`.

## Research lifecycle

1. Topic decomposition (`research_planner`)
2. Source discovery + ranking
3. Safe fetch (policy bounded)
4. Multi-agent swarm investigation
5. Contradiction detection
6. Synthesis + citations
7. Knowledge graph ingestion
8. Trend + belief updates

## APIs

- `GET /api/v1/runtime/knowledge`
- `POST /api/v1/runtime/knowledge/ingest`
- `GET /api/v1/runtime/research`
- `POST /api/v1/runtime/research/start|topic|verify`
- `GET /api/v1/runtime/world-model|beliefs|contradictions|trends|sources`
- `GET /api/v1/missions/{id}/knowledge|research|beliefs`

Legacy debate research: `GET /api/v1/runtime/research/debate`

## Safety model

- Read-only web by default
- Domain allow/deny + suspicious path blocking
- Robots.txt respect stub
- Rate limiting + crawl depth bounds
- Research budget per hour
- Harmful topic filtering
- Emergency stop integration
- No login/forms/purchases

## Streaming channels

`knowledge:runtime`, `research:runtime`, `beliefs:runtime`, `worldmodel:runtime`, `trends:runtime`

## Operator Console

`/runtime/knowledge`, `/runtime/research-fabric`, `/runtime/world-model`, `/runtime/beliefs`, `/runtime/contradictions`, `/runtime/trends`, `/runtime/sources`

## Scaling path

- SQLite → dedicated knowledge store
- Stub fetch → controlled Playwright/httpx with allowlist
- Local search → SearXNG/Brave API adapter (still policy bounded)
- Swarm agents → distributed worker research tasks
