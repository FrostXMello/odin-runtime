"""Tool capability definitions for intelligence layer."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ToolCapabilitySpec:
    capability: str
    tools: tuple[str, ...]
    description: str = ""
    constraints: dict[str, str] = field(default_factory=dict)


BUILTIN_CAPABILITIES: tuple[ToolCapabilitySpec, ...] = (
    ToolCapabilitySpec("filesystem.read", ("read_file", "list_directory"), "Read filesystem paths"),
    ToolCapabilitySpec("filesystem.write", ("write_file",), "Write filesystem paths"),
    ToolCapabilitySpec("python.safe", (), "Sandboxed Python execution"),
    ToolCapabilitySpec("shell.safe", ("execute_terminal",), "Controlled shell execution"),
    ToolCapabilitySpec("api.http", ("search_web",), "HTTP/API calls"),
    ToolCapabilitySpec("web.search", ("search_web",), "Web search"),
    ToolCapabilitySpec("workflow.execute", (), "Workflow orchestration steps"),
)


def capability_for_tool(tool_name: str) -> str | None:
    for spec in BUILTIN_CAPABILITIES:
        if tool_name in spec.tools:
            return spec.capability
    return None
