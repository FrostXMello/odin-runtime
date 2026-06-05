"""Intelligent tool registry — schemas, capabilities, health."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from odin_backend.core.tools.capabilities import BUILTIN_CAPABILITIES, capability_for_tool


@dataclass
class ToolSpec:
    name: str
    capability: str
    description: str = ""
    input_schema: dict[str, Any] = field(default_factory=dict)
    output_schema: dict[str, Any] = field(default_factory=dict)
    constraints: dict[str, Any] = field(default_factory=dict)
    healthy: bool = True
    confidence: float = 0.8

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "capability": self.capability,
            "description": self.description,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "constraints": self.constraints,
            "healthy": self.healthy,
            "confidence": self.confidence,
        }


class IntelligentToolRegistry:
    """Registers tools with capability advertisement and execution constraints."""

    def __init__(self, app: Any | None = None) -> None:
        self._app = app
        self._tools: dict[str, ToolSpec] = {}
        self._register_builtins()

    def _register_builtins(self) -> None:
        for spec in BUILTIN_CAPABILITIES:
            for tool_name in spec.tools:
                self.register(
                    ToolSpec(
                        name=tool_name,
                        capability=spec.capability,
                        description=spec.description,
                        constraints=dict(spec.constraints),
                    )
                )
        for cap in ("python.safe", "workflow.execute"):
            self.register(ToolSpec(name=cap, capability=cap, description=f"Direct {cap} execution"))

    def register(self, spec: ToolSpec) -> None:
        self._tools[spec.name] = spec
        if self._app and hasattr(self._app, "tool_registry"):
            legacy = self._app.tool_registry.get(spec.name)
            if legacy:
                schema = legacy.get_schema()
                spec.input_schema = schema.get("parameters", {})
                spec.description = schema.get("description", spec.description)

    def get(self, name: str) -> ToolSpec | None:
        return self._tools.get(name)

    def list_by_capability(self, capability: str) -> list[ToolSpec]:
        prefix = capability.split(".")[0]
        out: list[ToolSpec] = []
        for t in self._tools.values():
            if t.capability == capability or t.capability.startswith(f"{prefix}."):
                out.append(t)
        return sorted(out, key=lambda x: -x.confidence)

    def list_all(self) -> list[ToolSpec]:
        return list(self._tools.values())

    def advertise_capabilities(self) -> list[str]:
        return sorted({t.capability for t in self._tools.values()})

    async def health(self) -> dict[str, Any]:
        return {
            "tool_count": len(self._tools),
            "capabilities": self.advertise_capabilities(),
            "healthy": sum(1 for t in self._tools.values() if t.healthy),
        }

    def sync_from_legacy(self) -> int:
        if not self._app or not hasattr(self._app, "tool_registry"):
            return 0
        count = 0
        for entry in self._app.tool_registry.list_tools():
            name = entry.get("name") or entry.get("tool_name")
            if not name:
                continue
            cap = capability_for_tool(name) or "python.safe"
            self.register(
                ToolSpec(
                    name=name,
                    capability=cap,
                    description=entry.get("description", ""),
                    input_schema=entry.get("parameters", {}),
                )
            )
            count += 1
        return count
