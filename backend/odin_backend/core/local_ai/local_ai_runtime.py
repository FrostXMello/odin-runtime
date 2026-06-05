"""Production local AI stack orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.local_ai.gpu_allocator import GPUAllocator
from odin_backend.core.local_ai.model_hot_swap import ModelHotSwap
from odin_backend.core.local_ai.model_profiles import get_profile
from odin_backend.core.local_ai.quantization_profiles import profile_for_hardware
from odin_backend.core.local_ai.streaming_decoder import StreamingDecoder
from odin_backend.core.local_ai.token_accounting import TokenAccounting
from odin_backend.core.local_ai.unified_prompting import build_prompt


class LocalAIRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        vram = getattr(app.settings, "local_ai_vram_mb", 4096)
        ram = getattr(app.settings, "local_ai_ram_mb", 16384)
        self._gpu = GPUAllocator(vram_mb=vram)
        self._hot_swap = ModelHotSwap()
        self._tokens = TokenAccounting()
        self._hardware = profile_for_hardware(vram_mb=vram, ram_mb=ram)
        self._loaded: set[str] = set()

    async def connect(self) -> None:
        if getattr(self._app.settings, "local_ai_warm_on_startup", False):
            await self.warm_load(getattr(self._app.settings, "reasoning_model", "reasoning"))

    async def disconnect(self) -> None:
        for m in list(self._loaded):
            await self.evict(m)

    async def route_model(self, *, complexity: float = 0.5, token_budget: int = 4096) -> dict[str, Any]:
        if complexity > 0.7:
            role = "reasoning"
        elif complexity > 0.4:
            role = "code"
        else:
            role = "fast"
        profile = get_profile(role)
        model = getattr(self._app.settings, f"model_{role}" if role != "fast" else "fast_model", role)
        if token_budget < 2000:
            role = "fast"
            model = getattr(self._app.settings, "fast_model", "fast")
        return {"model": model, "profile": profile, "role": role}

    async def warm_load(self, model_name: str) -> dict[str, Any]:
        if not getattr(self._app.settings, "local_ai_enabled", False):
            return {"accepted": False, "reason": "local_ai_disabled"}
        est = self._gpu.estimate(model_name)
        if not est["fits"] and not self._hardware.get("cpu_fallback"):
            return {"accepted": False, "reason": "vram_insufficient", "estimate": est}
        if hasattr(self._app, "model_manager"):
            await self._app.model_manager.load(model_name)
        self._loaded.add(model_name)
        self._hot_swap.swap(model_name)
        return {"accepted": True, "model": model_name, "estimate": est}

    async def evict(self, model_name: str) -> dict[str, Any]:
        if hasattr(self._app, "model_manager"):
            await self._app.model_manager.unload(model_name)
        self._gpu.release(model_name)
        self._loaded.discard(model_name)
        return {"evicted": model_name}

    async def generate(self, *, prompt: str, template: str = "reasoning", stream: bool = False) -> dict[str, Any]:
        routed = await self.route_model(complexity=0.5)
        built = build_prompt(template=template, input_text=prompt)
        decoder = StreamingDecoder()
        text = f"[local_stub]{prompt[:80]}"
        if hasattr(self._app, "model_manager"):
            if stream:
                async for chunk in self._app.model_manager.runtime.infer_stream(
                    messages=built["messages"], model=routed["model"]
                ):
                    await decoder.emit(chunk)
                text = decoder.text()
            else:
                result = await self._app.model_manager.runtime.infer(
                    messages=built["messages"], model=routed["model"]
                )
                text = str(result)
        self._tokens.record(
            prompt_tokens=self._tokens.estimate_chars(prompt),
            completion_tokens=self._tokens.estimate_chars(text),
        )
        return {"model": routed["model"], "text": text, "streamed": stream}

    def snapshot(self) -> dict[str, Any]:
        provider = "mock"
        if hasattr(self._app, "model_manager"):
            provider = self._app.model_manager.status().get("provider", "mock")
        return {
            "provider": provider,
            "active_model": self._hot_swap.active,
            "loaded": list(self._loaded),
            "gpu": self._gpu.snapshot(),
            "hardware": self._hardware,
            "tokens": self._tokens.snapshot(),
        }
