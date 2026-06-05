# Distributed Cognitive Federation (Prompt 32)

Odin Runtime extends to a **local-first federated cognitive layer** where multiple Odin nodes cooperate with bounded autonomy, observability, and policy safety.

## Enable

```env
federation_enabled=true
federation_node_name=odin-local
federation_node_role=coordinator
federation_max_nodes=8
federation_min_trust_share=0.4
federation_shared_secret=local-only
```

Default: federation disabled. No unrestricted internet federation.

## Federation modes

| Mode | Description |
|------|-------------|
| `isolated` | No cross-node operations |
| `trusted_cluster` | Local trusted peers only |
| `supervised_mesh` | Operator-supervised multi-node mesh |
| `research_mesh` | Research-only cross-node reasoning |

## Architecture

| Layer | Path | App attribute |
|-------|------|---------------|
| Federation core | `core/federation/` | `federation_runtime` |
| Agent exchange | `core/federated_agents/` | `society_federation` |
| Governance | `core/federation_governance/` | `federation_governance` |
| Federated memory | `core/federated_memory/` | `federated_memory` |

## Node model

Each node stores: `node_id`, role, capabilities, topology metadata, health state, trust level, latency stats, active agent/mission counts.

SQLite table: `odin_federation_nodes`.

## APIs

- `GET /api/v1/runtime/federation`
- `GET /api/v1/runtime/federation/nodes`
- `GET /api/v1/runtime/federation/topology`
- `GET /api/v1/runtime/federation/trust`
- `POST /api/v1/runtime/federation/connect`
- `POST /api/v1/runtime/federation/disconnect`
- `GET /api/v1/missions/{id}/federation`

## Streaming

**Channels:** `federation:runtime`, `governance:runtime`

**Trace kinds:** `federation_node_connected`, `federation_node_disconnected`, `remote_reasoning_requested`, `remote_reasoning_completed`, `trust_score_changed`, `governance_violation`, `node_quarantined`, `knowledge_shared`

## Safety

- Authentication tokens per node
- Permission matrix (none → read → reason → delegate → admin)
- Quarantine and emergency shutdown
- Agents sandboxed to origin node
- All cross-node ops audited

## Operator Console

`/runtime/federation`, `/runtime/governance`, `/runtime/federated-memory`
