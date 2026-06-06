"""Recommended local model registry and fallback chains."""

from __future__ import annotations

from typing import Any

MODELS: dict[str, dict[str, Any]] = {
    "ultra_light": {"primary": "phi3:mini", "fallback": ["gemma:2b"], "embed": "nomic-embed-text"},
    "balanced": {"primary": "qwen2.5:7b", "fallback": ["mistral:7b", "phi3:mini"], "embed": "nomic-embed-text"},
    "performance": {"primary": "deepseek-r1:7b", "fallback": ["qwen2.5:7b"], "embed": "nomic-embed-text"},
    "overnight": {"primary": "phi3:mini", "fallback": ["gemma:2b"], "embed": "nomic-embed-text"},
}


def chain_for_mode(mode: str) -> list[str]:
    entry = MODELS.get(mode, MODELS["balanced"])
    return [entry["primary"], *entry["fallback"]]
