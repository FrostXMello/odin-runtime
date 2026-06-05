# PROJECT ODIN — Architecture

## Overview

ODIN is a modular, event-driven autonomous AI operating system. All major subsystems communicate through structured events, task queues, and schemas — never through tight agent-to-agent coupling.

## Core Layers

```
┌─────────────────────────────────────────────────────────┐
│  Electron + React Command Center (frontend)             │
└──────────────────────────┬──────────────────────────────┘
                           │ HTTP /api/v1
┌──────────────────────────▼──────────────────────────────┐
│  FastAPI Service                                        │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│  ODIN Orchestrator — plan · delegate · monitor          │
└─────┬──────────────────────────────────────────────┬──────┘
      │                                              │
┌─────▼─────┐  ┌──────────────┐  ┌──────────┐  ┌────▼────┐
│ Agent     │  │ Task Queue   │  │ Workflow │  │ Memory  │
│ Registry  │  │ (Redis)      │  │ Engine   │  │ (MIMIR) │
└─────┬─────┘  └──────┬───────┘  └──────────┘  └─────────┘
      │               │
┌─────▼───────────────▼───────────────────────────────────┐
│  Event Bus (Redis Pub/Sub)                              │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│  Tool Registry + Permission Service + Tool Executor     │
└─────────────────────────────────────────────────────────┘
```

## Agents

| Agent     | Role                                      |
|-----------|-------------------------------------------|
| ODIN      | Orchestrator — does not execute all work  |
| VALKYRIE  | Desktop automation, operations            |
| MIMIR     | Memory coordination                       |
| HUGIN     | Research, web gathering                   |
| MUNIN     | Analysis, reports                         |
| BROKK     | Engineering, code                         |
| HEIMDALL  | Security, permissions                     |

## Event Types

Canonical events include `task.created`, `task.completed`, `memory.updated`, `workflow.triggered`, `agent.failed`, `security.alert`, and `tool.denied`.

## Memory Tiers

1. **Short-term** — sessions, active workflows
2. **Semantic** — embeddings / vector (ChromaDB)
3. **Structured** — settings, permissions, schedules

## Security

Tools are classified: `SAFE`, `CONFIRM_REQUIRED`, `RESTRICTED`, `BLOCKED`. Human override is always available.

## Milestone 1 (Current)

- Electron shell + React UI
- FastAPI backend
- ODIN orchestrator + agent framework
- Redis event bus + task queue
- Tool registry + permissions
- Structured logging
