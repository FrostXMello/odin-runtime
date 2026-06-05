# Local AI Stack (v0.34)

Odin now includes a production local model runtime that keeps inference on-device and routes requests by hardware limits and reasoning needs.

## Modules

- `core/local_ai/model_profiles.py` — model capability profiles (fast, code, reasoning).
- `core/local_ai/quantization_profiles.py` — dynamic quantization presets by VRAM/RAM class.
- `core/local_ai/gpu_allocator.py` — GPU memory estimation and fit checks.
- `core/local_ai/context_manager.py` — adaptive context truncation.
- `core/local_ai/streaming_decoder.py` — token-by-token callback assembly.
- `core/local_ai/speculative_decoding.py` — speculative decode planning hooks.
- `core/local_ai/model_hot_swap.py` — active reasoning-model swap state.
- `core/local_ai/unified_prompting.py` + `prompt_templates.py` — shared prompt templates.
- `core/local_ai/token_accounting.py` — request token budgets and accounting snapshots.
- `core/local_ai/local_ai_runtime.py` — orchestrator mounted as `app.local_ai`.

## Runtime providers

The stack preserves Odin’s existing provider architecture and runs through local model backends:

- Ollama
- llama.cpp server
- MLX (Apple Silicon)

## Behavior

- Routes model selection by complexity, latency target, and token budget.
- Warm-loads models on startup when enabled.
- Evicts idle models and releases allocator state.
- Falls back to CPU inference when VRAM is insufficient and CPU fallback is allowed.
- Preserves streaming semantics via incremental decoder events.

## Configuration

```env
ODIN_LOCAL_AI_ENABLED=true
ODIN_LOCAL_AI_VRAM_MB=4096
ODIN_LOCAL_AI_RAM_MB=16384
ODIN_LOCAL_AI_WARM_ON_STARTUP=true
```

## API surface

- `GET /api/v1/runtime/local-ai`
- `POST /api/v1/runtime/local-ai/generate`

## Compatibility guarantees

- Local-first only.
- No cloud dependency required.
- Existing model manager and async runtime remain intact.
- Existing observability and streaming contracts remain additive.
