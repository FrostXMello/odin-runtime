# Self-Healing Execution (v0.35)

Recovers partially failed missions and stuck executions without rewriting orchestration.

## Modules

- `core/self_healing/self_healing_runtime.py` — orchestrator (`app.self_healing`)
- `core/self_healing/mission_salvage.py` — partial mission recovery
- `core/self_healing/dependency_healer.py` — blocked dependency resolution
- `core/self_healing/stuck_execution_resolver.py` — timeout sweeps

## Configuration

```env
ODIN_SELF_HEALING_ENABLED=true
```

## API

- `GET /api/v1/runtime/self-healing`
- `POST /api/v1/runtime/self-healing/heal`
