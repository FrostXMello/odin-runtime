"""
Agent-layer protocols — dependency inversion for tool execution.

Agents must not import tools.runtime.executor or core.app at module import time.
Concrete RuntimeToolExecutor is wired in OdinApplication._build() after all modules load.
"""

from odin_backend.shared.contracts.tool_executor import ToolExecutorProtocol

__all__ = ["ToolExecutorProtocol"]
