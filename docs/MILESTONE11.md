# Milestone 11 — Live Cognitive Runtime Activation

## Objective

End-to-end live execution: real signals → kernel reasoning → governor → tools → memory → graph.

## Components

| Path | Role |
|------|------|
| `core/model_router/` | `KernelModelRouter` — Gemini/DeepSeek/Qwen/Llama routing + fallback |
| `core/kernel/reasoning.py` | Sole LLM entry: `process_reasoning_request`, `execute_llm_planning` |
| `runtime/loop/engine.py` | `LiveExecutionLoop` — 12-step live cycle |
| `runtime/bootstrap/boot.py` | `OdinBootstrap` — ordered startup |
| `tools/execution/pipeline.py` | `LiveToolPipeline` — governor-gated tool chain |
| `core/bus/unified_bus.py` | Kernel lock, backpressure, `publish_fast` |

## Live cycle steps

1. ingest_signals → 2. kernel_interpret → 3. priority_evaluate → 4. coherence_validate → 5. governor_decide → 6. autonomy_scope → 7. model_router_plan → 8–9. tool/agent execution → 10. memory_update → 11. graph_update → 12. stability_tick (interval)

## API

- `GET /api/v1/live/status`
- `POST /api/v1/live/cognitive-cycle` — run full cycle with objective

## Config

```
ODIN_LIVE_LOOP_ENABLED=true
ODIN_LIVE_LOOP_INTERVAL_SECONDS=5.0
ODIN_MODEL_GEMINI=gemini-2.0-flash
ODIN_MODEL_DEEPSEEK_CODER=deepseek-coder
```

## Tests

```powershell
pytest tests/cognitive_cycle_test.py tests/test_milestone11.py -v
```

## Rules enforced

- Only kernel calls LLMs via `KernelModelRouter`
- Tools via `ExecutionContract` + governor + Heimdall
- No silent execution paths
- Live mind fields on `CognitiveState`: `reasoning_trace`, `model_used`, `decision_path`, `memory_delta`, `graph_delta`
