"""Streaming local inference runtime."""

from __future__ import annotations

import time
from typing import Any, AsyncIterator

from odin_backend.core.models.batching import InferenceBatcher
from odin_backend.core.models.context_windowing import fit_messages
from odin_backend.core.models.inference_router import InferenceRouter
from odin_backend.core.models.kv_cache import KVCache
from odin_backend.core.models.registry import LocalModelRegistry
from odin_backend.core.models.tokenizer import estimate_messages_tokens


class ModelRuntime:
    def __init__(self, registry: LocalModelRegistry, *, app: Any | None = None) -> None:
        self._registry = registry
        self._router = InferenceRouter(registry)
        self._batcher = InferenceBatcher(max_concurrent=2)
        self._cache = KVCache()
        self._app = app
        self._metrics: dict[str, int] = {"inferences": 0, "cancelled": 0, "truncated": 0}

    @property
    def metrics(self) -> dict[str, int]:
        return dict(self._metrics)

    @property
    def router(self) -> InferenceRouter:
        return self._router

    async def infer(
        self,
        *,
        messages: list[dict[str, str]],
        task_kind: str = "planning",
        model: str | None = None,
        temperature: float = 0.2,
        max_context_tokens: int = 8192,
        stream: bool = False,
        mission_id: str | None = None,
    ) -> str | AsyncIterator[str]:
        route = self._router.route_payload(task_kind=task_kind, payload={"context_tokens": estimate_messages_tokens(messages)})
        model_name = model or route["model"]
        profile = self._registry.get(model_name)
        window = profile.context_window if profile else max_context_tokens
        fitted, truncated = fit_messages(messages, max_tokens=window)
        if truncated:
            self._metrics["truncated"] += 1
            self._emit("context_truncated", {"model": model_name, "mission_id": mission_id})

        async def _run(req) -> str:
            if req.cancelled:
                raise RuntimeError("cancelled")
            self._emit("inference_started", {"model": model_name, "request_id": req.request_id, "mission_id": mission_id})
            start = time.perf_counter()
            provider = self._registry.provider
            if stream:
                raise RuntimeError("use infer_stream for streaming")
            text = await provider.complete(model=model_name, messages=fitted, temperature=temperature)
            latency = (time.perf_counter() - start) * 1000
            self._registry.record_latency(model_name, latency)
            self._metrics["inferences"] += 1
            self._emit(
                "inference_completed",
                {"model": model_name, "latency_ms": latency, "mission_id": mission_id},
                duration_ms=latency,
            )
            return text

        if stream:
            return self.infer_stream(
                messages=fitted,
                model=model_name,
                temperature=temperature,
                mission_id=mission_id,
            )
        return await self._batcher.submit(_run, model=model_name, priority=3)

    async def infer_stream(
        self,
        *,
        messages: list[dict[str, str]],
        model: str,
        temperature: float = 0.2,
        mission_id: str | None = None,
    ) -> AsyncIterator[str]:
        self._emit("inference_started", {"model": model, "stream": True, "mission_id": mission_id})
        start = time.perf_counter()
        provider = self._registry.provider
        async for token in provider.stream_complete(model=model, messages=messages, temperature=temperature):
            yield token
        latency = (time.perf_counter() - start) * 1000
        self._registry.record_latency(model, latency)
        self._metrics["inferences"] += 1
        self._emit("inference_completed", {"model": model, "stream": True, "latency_ms": latency}, duration_ms=latency)

    async def embed(self, texts: list[str], *, model: str | None = None) -> list[list[float]]:
        model_name = model or self._router.select_model(capability=__import__(
            "odin_backend.core.models.model_profiles", fromlist=["ModelCapabilityTag"]
        ).ModelCapabilityTag.EMBEDDING)
        return await self._registry.provider.embed(model=model_name, texts=texts)

    def cancel(self, request_id: str) -> bool:
        self._batcher.cancel(request_id)
        self._metrics["cancelled"] += 1
        return self._registry.provider.cancel(request_id)

    def _emit(self, kind_name: str, payload: dict, *, duration_ms: float | None = None) -> None:
        obs = getattr(self._app, "observability", None) if self._app else None
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="model_runtime", duration_ms=duration_ms)
