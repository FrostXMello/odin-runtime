"""Model orchestration helpers (Prompt 38)."""

from __future__ import annotations

from typing import Any


def route_reasoning(*, complexity: float, vram_mb: int, on_battery: bool) -> dict[str, Any]:
    if on_battery or vram_mb < 4096:
        model = "fast"
    elif complexity > 0.75:
        model = "reasoning"
    elif complexity > 0.4:
        model = "code"
    else:
        model = "fast"
    return {"model": model, "complexity": complexity, "compressed_context": on_battery}


def lightweight_plan(*, goal: str) -> dict[str, Any]:
    return {"goal": goal, "steps": ["analyze", "plan", "execute"], "model": "fast"}


def schedule_deep_reasoning(*, queue_depth: int, vram_free_mb: int) -> dict[str, Any]:
    allowed = vram_free_mb > 2048 and queue_depth < 3
    return {"allowed": allowed, "queue_depth": queue_depth}


def specialize_inference(*, task: str) -> str:
    if "code" in task or "debug" in task:
        return "code"
    if "research" in task or "analyze" in task:
        return "reasoning"
    return "fast"


def bind_memory(*, model: str, memory_ids: list[str]) -> dict[str, Any]:
    return {"model": model, "bound_memories": len(memory_ids), "ids": memory_ids[:10]}
