"""RAM-aware model scheduling."""

from __future__ import annotations

from typing import Any

from odin_backend.core.resources.gpu_monitor import gpu_status
from odin_backend.core.resources.inference_limits import InferenceLimiter
from odin_backend.core.resources.model_eviction import ModelEvictionPolicy
from odin_backend.core.resources.ram_monitor import memory_pressure, ram_status


class ModelResourceScheduler:
    def __init__(self, app: Any) -> None:
        self._app = app
        max_inf = getattr(app.settings, "max_concurrent_inference", 2)
        self._limiter = InferenceLimiter(max_concurrent=max_inf)
        self._eviction = ModelEvictionPolicy()

    async def ensure_capacity(self, *, model_name: str, ram_mb: int) -> dict[str, Any]:
        pressure = memory_pressure()
        ram = ram_status()
        if pressure > 0.85 and ram.get("available_mb", 0) < ram_mb:
            loaded = [p.name for p in self._app.model_manager.registry.loaded_models()]
            evict = self._eviction.candidates(loaded)
            if evict:
                await self._eviction.evict(self._app, evict[:1])
        return {"pressure": pressure, "ram": ram, "gpu": gpu_status()}

    async def load_with_budget(self, model_name: str) -> dict[str, Any]:
        profile = self._app.model_manager.registry.get(model_name)
        ram_need = profile.ram_mb_estimate if profile else 4096
        status = await self.ensure_capacity(model_name=model_name, ram_mb=ram_need)
        prof = await self._app.model_manager.load(model_name)
        self._eviction.touch(model_name)
        return {"profile": prof.model_dump(mode="json"), "resources": status}

    def status(self) -> dict[str, Any]:
        return {
            "ram": ram_status(),
            "gpu": gpu_status(),
            "memory_pressure": memory_pressure(),
            "max_concurrent_inference": self._limiter.max_concurrent,
            "loaded": [p.name for p in self._app.model_manager.registry.loaded_models()],
        }
