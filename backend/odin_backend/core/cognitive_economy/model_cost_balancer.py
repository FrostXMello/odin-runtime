"""Dynamic model selection by cost."""

from __future__ import annotations

from typing import Any

MODEL_COSTS = {"mock": 0.1, "llama3.2": 0.5, "qwen2.5": 0.6, "deepseek-r1": 0.8}


def select_model(*, mode: str, task_complexity: float) -> str:
    if mode == "low_resource":
        return "mock"
    if mode == "high_performance" or task_complexity > 0.7:
        return "deepseek-r1"
    return "qwen2.5"
