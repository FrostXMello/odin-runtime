# Persistent Agent Society + Long-Running Cognition (Prompt 31)

Odin Runtime extends from autonomous execution loops into a **persistent multi-agent cognitive society** with specialized identities, memory continuity, evolving expertise, and cooperative reasoning.

## Enable

```env
agent_society_enabled=true
agent_society_max_agents=12
agent_message_rate_per_minute=30
agent_debate_max_depth=8
```

Default: society disabled. All cognition and inter-agent communication remain observable, bounded, and policy-constrained.

## Architecture

| Layer | Path | App attribute |
|-------|------|---------------|
| Society orchestrator | `core/agent_society/society_coordinator.py` | `agent_society` |
| Persistent identity | `core/agent_society/persistent_agents.py` | (via `agent_society`) |
| Continuity | `core/agent_society/continuity_state.py` | (via `agent_society`) |
| Objectives | `core/agent_society/objective_chains.py` | (via `agent_society`) |
| Collaboration | `core/agent_society/collaboration_graph.py`, `debate_sessions.py`, `delegation_planner.py` | (via `agent_society`) |
| Governance | `core/agent_society/society_governance.py` | (via `agent_society`) |
| Internal messaging | `core/agent_messages/` | `agent_messages` |
| Peer learning | `core/learning_society/` | `peer_learning` |

**Preserved:** dispatcher, async runtime, MissionExecutionBridge, distributed queues, execution engine, cognition runtime, action engine, knowledge fabric, streaming contracts, existing operator routes.

## Agent identity model

Each persistent agent stores:

- identity (`agent_id`, `name`, `role`)
- capabilities and expertise domains
- confidence and behavioral traits (bounded ±0.15 drift)
- collaboration preferences and communication style
- long-term objectives and reasoning tendencies
- performance history and memory embeddings

SQLite tables: `odin_society_agents`, `odin_agent_continuity`, `odin_society_objectives`.

## Continuity model

On startup, agents restore from SQLite checkpoints:

1. Load persisted identity from `odin_society_agents`
2. Restore working memory snapshot from `odin_agent_continuity`
3. Emit `continuity_restored` trace
4. Resume unfinished objectives and active thought contexts

Checkpoints capture thought state, memory fragments, and objective references.

## Specialization evolution

Expertise evolves through:

- successful missions (`record_outcome`)
- validated research outcomes
- collaboration quality signals
- failure recovery patterns

Bounded growth via `personality_bounds.bounded_update` and periodic `rebalance()` — no runaway reinforcement, confidence decay on failures.

Example specializations: planning specialist, infrastructure optimizer, research analyst, failure diagnostician, execution strategist, memory curator.

## Collaborative society

| Component | Role |
|-----------|------|
| `SocietyCoordinator` (`AgentSocietyRuntime`) | Main orchestrator |
| `TaskCouncil` | Role negotiation |
| `ConsensusEngine` | Weighted confidence voting |
| `DebateSessions` | Structured multi-agent debate |
| `DelegationPlanner` | Task handoff between agents |
| `CollaborationGraph` | Relationship edges and retrospectives |
| `CognitiveTeams` | Temporary task groups (Research Squad, Planning Committee, etc.) |

## Internal communication fabric

`core/agent_messages/` provides:

- `message_bus.py` — observable, persisted, streamable message routing
- `negotiation_protocol.py` — role and responsibility negotiation
- `structured_dialogue.py` — typed dialogue turns
- `reasoning_exchange.py` — hypothesis proposal and critique
- `internal_mailbox.py` — per-agent inbox
- `coordination_memory.py` — shared coordination context

## Long-horizon objectives

Agents own objective chains with:

- subgoal decomposition
- milestone tracking (`pending`, `active`, `deferred`, `completed`)
- deferred cognition queue
- revisit scheduling on restart

## Learning society

`core/learning_society/` implements:

- peer teaching (`peer_learning.py`)
- mentor selection
- expertise transfer
- strategy distillation
- reasoning pattern library
- collaborative training sessions

No direct code rewriting — learning distills patterns and strategies only.

## World model integration

`record_outcome` ingests agent performance facts into `knowledge_runtime` as beliefs (`entity: agent:{id}`). Agents maintain personal expertise maps; shared beliefs flow through the knowledge fabric and contradiction engine.

## APIs

Society endpoints use `/runtime/society/*` to avoid conflicts with existing autonomy and collaboration routes.

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/runtime/agents` | Cognitive agents + `society_agents` |
| GET | `/api/v1/runtime/society` | Society snapshot |
| GET | `/api/v1/runtime/society/agents` | Persistent agents |
| POST | `/api/v1/runtime/society/agents/spawn` | Spawn agent |
| GET | `/api/v1/runtime/society/collaboration` | Collaboration graph |
| GET | `/api/v1/runtime/society/objectives` | Society objectives |
| POST | `/api/v1/runtime/society/objectives/create` | Create objective |
| GET/POST | `/api/v1/runtime/society/dialogues` | Dialogues and debates |
| GET/POST | `/api/v1/runtime/society/delegation` | Delegations |
| GET | `/api/v1/runtime/society/expertise` | Expertise heatmap |

Mission APIs:

- `GET /api/v1/missions/{id}/collaboration`
- `GET /api/v1/missions/{id}/dialogues`
- `GET /api/v1/missions/{id}/delegation`

## Streaming

**Trace kinds:** `agent_spawned`, `expertise_updated`, `delegation_created`, `debate_started`, `consensus_reached`, `collaboration_formed`, `objective_assigned`, `continuity_restored`, `reasoning_shared`, `agent_reflection_generated`

**Channels:** `agents:runtime`, `society:runtime`, `collaboration:runtime`, `objectives:runtime`, `dialogues:runtime`

## Operator Console

| Page | Purpose |
|------|---------|
| `/runtime/agents` | Cognitive + society agents (extended API) |
| `/runtime/society` | Live society snapshot |
| `/runtime/collaboration` | Human collaboration (preserved) |
| `/runtime/objectives` | Autonomy objectives (preserved) |
| `/runtime/dialogues` | Debate inspector |
| `/runtime/delegation` | Delegation timeline |
| `/runtime/expertise` | Expertise heatmap |

## Safety + governance

- Agent population limits (`agent_society_max_agents`)
- Society disabled by default (`agent_society_enabled=false`)
- Communication rate limits per agent per minute
- Recursive debate depth guard (`agent_debate_max_depth`)
- Emergency stop integration (blocks spawn)
- Bounded specialization drift (±0.15)
- No unrestricted self-modification or internet autonomy
- All inter-agent messages persisted and replayable

## Scaling path

- SQLite → dedicated agent identity store
- In-memory collaboration graph → graph database
- Message bus → durable event log with replay
- Cognitive teams → distributed task queues
- Expertise heatmap → vector index for mentor matching

## Future upgrades (Prompt 32+)

- Cross-mission agent memory federation
- Supervised long-horizon autonomy chains
- Operator-driven agent dormancy and archival
- Federated debate across runtime instances
- Expertise-based model routing
