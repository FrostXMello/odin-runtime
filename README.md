# Odin Runtime

**Production Cognitive Infrastructure**

Odin Runtime is a local-first cognitive operating system for daily engineering work. v0.64 stabilizes the existing runtime for continuous operation: reduced idle resource usage, faster startup, reliable SQLite persistence, stream efficiency, and production-grade diagnostics.

This release does not expand cognitive features. It hardens what already exists.

---

## What Changed in v0.64

| Area | Improvement |
|------|-------------|
| Idle resources | Low-power coordination, background activity reduction |
| Startup | Lazy runtime loading, startup timing metrics |
| Streams | Compression, batching, stale channel pruning |
| SQLite | Compaction, rolling checkpoint retention (200 max) |
| Memory | Adaptive pressure optimization, surface compression |
| Cleanup | Orphan state, replay windows, overlay cache |
| Observability | Runtime metrics, startup profiler, throughput tracking |

---

## Production Modules

| Module | Handle | Purpose |
|--------|--------|---------|
| `runtime_diagnostics` | `app.runtime_diagnostics` | Health inspection, sync validation, checkpoint integrity |
| `resource_optimization` | `app.resource_optimization` | Memory/GPU balancing, low-power coordination |
| `stream_management` | `app.stream_management` | Stream compression, prioritization, pruning |
| `session_persistence_v2` | `app.session_persistence_v2` | Cross-restart recovery, SQLite compaction |
| `runtime_cleanup` | `app.runtime_cleanup` | Orphan cleanup, replay cache, background scheduling |
| `production_observability` | `app.production_observability` | Metrics, profiling, startup timing |

---

## Operational Guarantees

| Guarantee | Implementation |
|-----------|----------------|
| Local-first | All persistence and metrics stay on-device |
| Transparent monitoring | Diagnostics emit trace events and domain channels |
| Approval-gated execution | Existing supervision gates preserved |
| Bounded growth | Checkpoint retention, batch limits, cleanup scheduling |
| Reversible | Compaction and cleanup are non-destructive by default |
| Backward compatible | No API breaks, no dispatcher rewrites |

---

## Startup & Runtime Lifecycle

```mermaid
flowchart LR
    START[Application Start] --> LAZY[Lazy Runtime Loading]
    LAZY --> HYDRATE[Deferred UI Hydration]
    HYDRATE --> RUN[Normal Operation]
    RUN --> DIAG[Diagnostics Loop]
    DIAG --> CLEAN[Background Cleanup]
    CLEAN --> LOW[Low-Power Idle]
```

With `ODIN_STARTUP_OPTIMIZATION_ENABLED=1`, startup timing is measured and reported via `production_observability`.

---

## Maintenance Workflows

### Daily operation

1. Enable production hardening flags in `.env`
2. Monitor `/runtime-health` and `/runtime-metrics`
3. Run passive cleanup on schedule (automatic when enabled)

### After crash or restart

1. `POST /session-persistence-v2/recover` — restore interrupted runtime
2. `GET /runtime-diagnostics/health` — verify integrity
3. `POST /runtime-cleanup/run` — clear stale state

### Low-power / overnight

1. Set `ODIN_LOW_POWER_COORDINATION=1`
2. `POST /resource-optimization/low-power`
3. Cleanup mode: `overnight`

---

## Hardware Profiles

| Profile | GTX 1650 Ti | 16GB RAM | M-series MacBook |
|---------|-------------|----------|------------------|
| `compact` | Minimal render budget | Aggressive compaction | Battery throttle |
| `balanced` | Standard GPU balance | Default retention | Default coordination |
| `engineering` | Full diagnostics | Deep inspection | Extended metrics |
| `low_power` | Overlay throttling | Background reduction | Overnight cleanup |

Configure via `ODIN_RESOURCE_PROFILE=balanced`.

---

## Streaming Topology

```
runtime (global)
├── runtime-diagnostics:runtime
├── resource-optimization:runtime
├── stream-management:runtime
├── session-persistence-v2:runtime
├── runtime-cleanup:runtime
├── production-observability:runtime
└── ... (existing era channels preserved)
```

---

## APIs

```
/api/v1/runtime/
├── runtime-diagnostics/health
├── runtime-diagnostics/report
├── resource-optimization/rebalance
├── resource-optimization/low-power
├── stream-management/compress
├── stream-management/prune
├── session-persistence-v2/recover
├── session-persistence-v2/compact
├── runtime-cleanup/run
├── runtime-cleanup/status
├── production-observability/metrics
├── production-observability/profile
├── runtime-health
├── startup-profiler
├── stream-throughput
└── runtime-metrics
```

---

## Operator Console

| Page | Purpose |
|------|---------|
| `/runtime-diagnostics` | Health inspection and reports |
| `/runtime-health` | Lightweight health matrix |
| `/stream-management` | Stream compression and pruning |
| `/stream-throughput` | Throughput measurement |
| `/resource-optimization` | Memory and render budgeting |
| `/session-persistence` | Cross-restart recovery |
| `/runtime-cleanup` | Cleanup status and scheduling |
| `/production-observability` | Production metrics |
| `/startup-profiler` | Startup timing waterfall |
| `/runtime-metrics` | Operational load tracking |

Frontend panels: `frontend/cognitive_workspace/src/production/ProductionPanels.tsx`

---

## Environment Configuration

```env
ODIN_RUNTIME_DIAGNOSTICS_ENABLED=1
ODIN_RESOURCE_OPTIMIZATION_ENABLED=1
ODIN_STREAM_MANAGEMENT_ENABLED=1
ODIN_SESSION_PERSISTENCE_V2_ENABLED=1
ODIN_RUNTIME_CLEANUP_ENABLED=1
ODIN_PRODUCTION_OBSERVABILITY_ENABLED=1
ODIN_RESOURCE_PROFILE=balanced
ODIN_STREAM_COMPRESSION_MODE=adaptive
ODIN_LOW_POWER_COORDINATION=1
ODIN_STARTUP_OPTIMIZATION_ENABLED=1
ODIN_SQLITE_COMPACTION_ENABLED=1
```

---

## Scaling Limits

| Limit | Value |
|-------|-------|
| Stream batch size | 64 |
| Session checkpoints | 200 (rolling) |
| Diagnostic reports | 20 (rolling) |
| Cleanup modes | passive / aggressive / overnight |

Additional: adaptive render throttling, bounded replay retention, SQLite VACUUM scheduling, overlay render throttling, runtime cooldown scheduling, adaptive event coalescing.

---

## Runtime Evolution

| Version | Focus |
|---------|-------|
| v0.60 | Unified Cognitive Command Center |
| v0.61 | Closed-Loop Predictive Recovery |
| v0.62 | Multi-Operator Collaborative Cognition |
| v0.63 | Real-Time Rollback DAG Animation Engine |
| **v0.64** | **Production Hardening** |

---

## Future Stabilization Roadmap

| Version | Focus |
|---------|-------|
| v0.65 | Unified cinematic operational desktop |
| v0.66 | Predictive mission continuity forecasting |
| v0.67 | Persistent collaborative cognition memory fabric |
| v0.68 | Real-time cognitive execution simulation engine |

---

## Safety

Odin v0.64 adds monitoring and cleanup without removing supervision. No hidden automation, no cloud dependencies, no unrestricted OS control. All cleanup and recovery paths remain operator-visible and reversible.

---

<p align="center">
  <strong>Odin Runtime v0.64</strong> — Production Hardening<br>
  Local-first · Operator-supervised · Bounded · Maintainable
</p>
