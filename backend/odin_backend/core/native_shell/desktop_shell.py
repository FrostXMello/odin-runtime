"""Lightweight desktop shell adapter."""
from __future__ import annotations
import platform
from typing import Any

PLATFORMS = ("windows", "darwin", "linux")

def detect_platform() -> str:
    s = platform.system().lower()
    if "windows" in s:
        return "windows"
    if "darwin" in s:
        return "darwin"
    return "linux"

def shell_state(*, visible: bool = True) -> dict[str, Any]:
    return {"platform": detect_platform(), "visible": visible, "local_only": True, "adapter": "lightweight"}
