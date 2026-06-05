"""Model load/unload lifecycle manager."""

from __future__ import annotations

from typing import Any

from odin_backend.config import Settings
from odin_backend.core.models.model_profiles import ModelProfile
from odin_backend.core.models.model_runtime import ModelRuntime
from odin_backend.core.models.registry import LocalModelRegistry


class ModelManager:
    def __init__(self, settings: Settings, registry: LocalModelRegistry, app: Any | None = None) -> None:
        self._settings = settings
        self._registry = registry
        self._runtime = ModelRuntime(registry, app=app)
        self._app = app

    @property
    def registry(self) -> LocalModelRegistry:
        return self._registry

    @property
    def runtime(self) -> ModelRuntime:
        return self._runtime

    async def connect(self) -> None:
        health = await self._registry.provider.health_check()
        if not health.get("healthy") and self._settings.model_provider != "mock":
            # Graceful degradation to mock for offline laptops
            from odin_backend.core.models.providers.mock import MockProvider

            self._registry._active_provider = MockProvider()

    async def disconnect(self) -> None:
        for prof in list(self._registry.loaded_models()):
            await self.unload(prof.name)

    async def load(self, model_name: str) -> ModelProfile:
        profile = await self._registry.provider.load_model(model_name)
        self._registry.register_profile(profile)
        self._emit("model_loaded", {"model": model_name})
        return profile

    async def unload(self, model_name: str) -> bool:
        ok = await self._registry.provider.unload_model(model_name)
        prof = self._registry.get(model_name)
        if prof:
            prof.loaded = False
        return ok

    async def list_available(self) -> list[str]:
        return await self._registry.provider.list_models()

    def status(self) -> dict[str, Any]:
        return {
            "provider": self._registry.provider.name,
            "registry": self._registry.snapshot(),
            "runtime_metrics": self._runtime.metrics,
        }

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None) if self._app else None
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="model_manager")
