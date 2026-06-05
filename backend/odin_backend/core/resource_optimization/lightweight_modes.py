"""Low-resource operating modes."""

from __future__ import annotations

from typing import Any

MODES = ("normal", "lightweight", "degraded", "minimal")


def mode_config(mode: str) -> dict[str, Any]:
    configs = {
        "normal": {"max_context": 8192, "max_models": 2, "background": True},
        "lightweight": {"max_context": 4096, "max_models": 1, "background": False},
        "degraded": {"max_context": 2048, "max_models": 1, "background": False},
        "minimal": {"max_context": 1024, "max_models": 0, "background": False},
    }
    return configs.get(mode, configs["lightweight"])
