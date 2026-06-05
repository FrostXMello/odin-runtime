"""Capability definitions for executor registry."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CapabilitySpec:
    name: str
    description: str = ""
    sandbox_required: bool = True
    default_timeout_seconds: float = 120.0
    max_concurrency: int = 2


CAPABILITIES: dict[str, CapabilitySpec] = {
    "filesystem.read": CapabilitySpec("filesystem.read", sandbox_required=True, max_concurrency=4),
    "filesystem.write": CapabilitySpec("filesystem.write", sandbox_required=True, max_concurrency=2),
    "shell.safe": CapabilitySpec("shell.safe", sandbox_required=True, default_timeout_seconds=60),
    "python.safe": CapabilitySpec("python.safe", sandbox_required=True, default_timeout_seconds=120),
    "api.internal": CapabilitySpec("api.internal", sandbox_required=False, max_concurrency=8),
    "workflow.execute": CapabilitySpec(
        "workflow.execute", sandbox_required=False, default_timeout_seconds=300, max_concurrency=2
    ),
}


def infer_execution_type(capability: str) -> str:
    if capability.startswith("python"):
        return "python"
    if capability.startswith("shell"):
        return "shell"
    if capability.startswith("filesystem"):
        return "file"
    if capability.startswith("workflow"):
        return "workflow"
    return "python"
