# Local Cognition Layer (v0.26)

Odin’s local-first cognitive runtime runs reasoning, reflection, and memory-grounded planning entirely on-device. No cloud dependency is required.

## Architecture

```
core/models/          Local model registry, providers, inference runtime
core/agents/          Cognitive agents (planner, critic, memory, …)
core/cognition/
  reasoning/          Memory-grounded context assembly
  reflection/         Self-critique with recursion guards
core/embeddings/      Local embeddings + SQLite vector store
core/resources/       RAM/GPU-aware model scheduling
```

## Providers

| Provider | Use case |
|----------|----------|
| `mock` | Tests, offline dev (default in CI) |
| `ollama` | General local models (GGUF via Ollama) |
| `llamacpp` | llama.cpp HTTP server |
| `mlx` | Apple Silicon optimized inference |

## Configuration

```env
ODIN_MODEL_PROVIDER=ollama
ODIN_MODEL_BASE_URL=http://127.0.0.1:11434
ODIN_EMBEDDING_MODEL=nomic-embed-text
ODIN_REASONING_MODEL=deepseek-r1:7b
ODIN_FAST_MODEL=phi3:mini
ODIN_LOCAL_COGNITION_ENABLED=true
ODIN_REFLECTION_MAX_DEPTH=2
ODIN_MAX_CONCURRENT_INFERENCE=2
```

## APIs

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/runtime/models` | Registry snapshot |
| GET | `/api/v1/runtime/models/loaded` | Loaded models |
| POST | `/api/v1/runtime/models/load` | Load with RAM budget |
| POST | `/api/v1/runtime/models/unload` | Unload model |
| GET | `/api/v1/runtime/agents` | Cognitive agents |
| GET/POST | `/api/v1/runtime/reasoning` | Pipeline status / run |
| GET/POST | `/api/v1/runtime/reflection` | Reflection config / run |
| GET | `/api/v1/runtime/embeddings` | Embedding index metrics |
| GET | `/api/v1/runtime/resources` | RAM/GPU pressure |
| GET | `/api/v1/missions/{id}/reasoning-chain` | Agent reasoning chain |
| GET | `/api/v1/missions/{id}/reflection` | Mission reflections |
| GET | `/api/v1/missions/{id}/memory-grounding` | Memory context block |

## Streaming channels

- `models:runtime` — load/inference events
- `reasoning:runtime` — memory grounding, context truncation
- `reflection:runtime` — critique, contradiction, hallucination risk
- `agents:runtime` — reasoning chain extensions

## Operator Console

- `/runtime/models` — model registry & load state
- `/runtime/agents` — cognitive agent roster
- `/runtime/reasoning` — pipeline metrics
- `/runtime/reflection` — guard configuration
- `/runtime/resources` — RAM/GPU pressure

## Design constraints

- **Local-first**: degrades to `MockProvider` when Ollama is unreachable
- **No autonomous loops**: reflection depth and time budgets are capped
- **Additive only**: existing `local_models`, mission runtime, and streaming contracts are preserved
- **Consumer hardware**: eviction and inference throttling target 16–32 GB RAM laptops

## Tests

```bash
cd odin/backend
pytest tests/test_local_cognition.py -q
```
