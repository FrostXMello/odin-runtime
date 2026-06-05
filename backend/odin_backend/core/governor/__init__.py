"""
Governor package.

Keep this __init__ free of heavy imports. Previously it imported ExecutionGovernor
at load time, which forced kernel/context_graph while tools.runtime was still loading.

Import explicitly:
  from odin_backend.core.governor.decisions import ExecutionRequest
  from odin_backend.core.governor.governor import ExecutionGovernor
"""

from typing import Any

__all__ = [
    "ExecutionGovernor",
    "ExecutionRequest",
    "GovernorDecision",
    "GovernorDecisionType",
]


def __getattr__(name: str) -> Any:
    if name == "ExecutionGovernor":
        from odin_backend.core.governor.governor import ExecutionGovernor

        return ExecutionGovernor
    if name in ("ExecutionRequest", "GovernorDecision", "GovernorDecisionType"):
        from odin_backend.shared.contracts import governance as g

        return getattr(g, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
