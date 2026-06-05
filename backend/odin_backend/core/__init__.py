"""
Application core package.

Do NOT import OdinApplication here. core/__init__.py previously imported app.py
at package load, creating a cycle:

  agents.base → tools.runtime → core.__init__ → core.app → agents.registry → agents.base

Use: from odin_backend.core.app import OdinApplication
"""

from typing import Any

__all__ = ["OdinApplication", "get_app"]


def __getattr__(name: str) -> Any:
    if name in ("OdinApplication", "get_app"):
        from odin_backend.core.app import OdinApplication, get_app

        return OdinApplication if name == "OdinApplication" else get_app
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
