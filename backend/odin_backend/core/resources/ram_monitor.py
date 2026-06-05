"""RAM monitoring for constrained laptops."""

from __future__ import annotations

import os
from typing import Any


def ram_status() -> dict[str, Any]:
    try:
        import psutil

        vm = psutil.virtual_memory()
        return {
            "total_mb": int(vm.total / (1024 * 1024)),
            "available_mb": int(vm.available / (1024 * 1024)),
            "percent_used": vm.percent,
        }
    except ImportError:
        # Fallback without psutil
        return {"total_mb": 16384, "available_mb": 8192, "percent_used": 50.0, "estimated": True}


def memory_pressure() -> float:
    st = ram_status()
    return float(st.get("percent_used", 50.0)) / 100.0
