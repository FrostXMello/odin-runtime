# Milestone 3 — Persistent Intelligence + Real-Time Operations

## New Systems

### Persistent Runtime (`runtime/`)
- **RuntimeSupervisor** — lifecycle, health loops, recovery
- **AgentRuntimeRegistry** — heartbeats, health, active workflows
- **HeartbeatMonitor** — periodic agent heartbeats
- **HealthChecker** + **RecoveryManager** — stale detection, auto-recovery signals

### Background Watchers (`watchers/`)
- **HuginWatcher** — trend/news monitoring (insights only)
- **FafnirWatcher** — market watch placeholders
- **HeimdallWatcher** — security anomaly detection from audit log
- Emits `watcher.insight` and `recommendation.created` — **never executes dangerous actions**

### Browser Intelligence (`browser/`)
- **CDPClient** — Chrome DevTools Protocol (`/json/list`)
- **BrowserIntelligenceService** — session analysis, research clusters, insights
- `get_browser_tabs` tool uses real CDP when Chrome runs with `--remote-debugging-port=9222`

### Parallel Workflow (`workflows/dag_runner.py`)
- DAG level-based execution with `asyncio.gather`
- Modes: `sequential` | `parallel` | `hybrid`
- Step `depends_on: [1, 2]` supported

### Cognition Streaming (`cognition/stream.py`)
- Real-time `cognition.progress` events
- Integrated into reasoning + workflow execution

### Advanced MIMIR
- **MemoryScorer** — recency, frequency, project relevance
- **MemoryProject** clusters (ODIN, DYNACI, FINANCE, etc.)
- **MemorySummarizer** — workflow/project summaries

### Context (`context/service.py`)
- Opt-in (`ODIN_CONTEXT_AWARENESS_ENABLED`)
- Tracks project, workflow, application (transparent)

### Voice Foundation (`voice/`)
- Push-to-talk sessions only (`ODIN_VOICE_ENABLED`)
- Faster-Whisper STT + Piper TTS (optional deps)
- Streaming cognition chunks via `voice.chunk` events

### Observability
- **MetricsCollector** — counters, latency histograms
- **TraceContext** — trace_id, workflow_id, execution_id, correlation_id

## API

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/runtime/status` | Supervisor status |
| `GET /api/v1/runtime/agents` | Runtime agent registry |
| `GET /api/v1/browser/session` | CDP session analysis |
| `GET /api/v1/cognition/recent` | Cognition stream buffer |
| `PATCH /api/v1/context` | Opt-in context update |
| `GET /api/v1/memory/clusters` | Project memory domains |
| `GET /api/v1/watchers/insights/recent` | Watcher insights |
| `GET /api/v1/observability/metrics` | Runtime metrics |

## Configuration

```env
ODIN_RUNTIME_ENABLE_BACKGROUND_LOOPS=true
ODIN_CHROME_CDP_URL=http://127.0.0.1:9222
ODIN_CONTEXT_AWARENESS_ENABLED=false
ODIN_VOICE_ENABLED=false
ODIN_WORKFLOW_MAX_PARALLEL_STEPS=5
```

Chrome CDP: launch with `chrome.exe --remote-debugging-port=9222`
