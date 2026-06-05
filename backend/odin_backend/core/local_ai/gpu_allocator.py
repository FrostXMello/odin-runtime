"""GPU memory estimation and allocation."""

from __future__ import annotations

from typing import Any


class GPUAllocator:
    def __init__(self, *, vram_mb: int = 4096) -> None:
        self._vram_mb = vram_mb
        self._allocated: dict[str, int] = {}

    def estimate(self, model_name: str, *, size_mb: int = 1024) -> dict[str, Any]:
        used = sum(self._allocated.values())
        available = max(0, self._vram_mb - used)
        fits = size_mb <= available
        return {"model": model_name, "size_mb": size_mb, "available_mb": available, "fits": fits}

    def allocate(self, model_name: str, size_mb: int) -> bool:
        est = self.estimate(model_name, size_mb=size_mb)
        if not est["fits"]:
            return False
        self._allocated[model_name] = size_mb
        return True

    def release(self, model_name: str) -> None:
        self._allocated.pop(model_name, None)

    def snapshot(self) -> dict[str, Any]:
        return {"vram_mb": self._vram_mb, "allocated": dict(self._allocated)}
