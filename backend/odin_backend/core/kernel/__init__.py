"""
Cognitive kernel package — lazy exports to avoid import cycles with orchestrator/agents.

Import explicitly:
  from odin_backend.core.kernel.kernel import OdinCognitiveKernel
  from odin_backend.core.kernel.state import CognitiveState
"""

from typing import Any

__all__ = ["OdinCognitiveKernel", "CognitiveState"]


def __getattr__(name: str) -> Any:
    if name == "OdinCognitiveKernel":
        from odin_backend.core.kernel.kernel import OdinCognitiveKernel

        return OdinCognitiveKernel
    if name == "CognitiveState":
        from odin_backend.core.kernel.state import CognitiveState

        return CognitiveState
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
