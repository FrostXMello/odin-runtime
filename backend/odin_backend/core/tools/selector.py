"""Tool selection with confidence ranking and fallbacks."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from odin_backend.core.tools.registry import IntelligentToolRegistry, ToolSpec


@dataclass
class ToolSelection:
    tool: str | None
    capability: str
    confidence: float
    alternatives: list[dict[str, Any]] = field(default_factory=list)
    rationale: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool": self.tool,
            "capability": self.capability,
            "confidence": self.confidence,
            "alternatives": self.alternatives,
            "rationale": self.rationale,
        }


class ToolSelector:
    def __init__(self, registry: IntelligentToolRegistry) -> None:
        self._registry = registry
        self._decisions: list[ToolSelection] = []

    def select(
        self,
        capability: str,
        *,
        params: dict[str, Any] | None = None,
        memory_bias: dict[str, float] | None = None,
    ) -> ToolSelection:
        candidates = self._registry.list_by_capability(capability)
        if not candidates and capability == "python.safe":
            sel = ToolSelection(tool=None, capability=capability, confidence=0.85, rationale="direct execution")
            self._decisions.append(sel)
            return sel

        scored: list[tuple[float, ToolSpec]] = []
        for spec in candidates:
            score = spec.confidence
            if memory_bias and spec.name in memory_bias:
                score += memory_bias[spec.name] * 0.15
            if not spec.healthy:
                score -= 0.5
            scored.append((score, spec))

        scored.sort(key=lambda x: -x[0])
        if not scored:
            sel = ToolSelection(
                tool=None,
                capability=capability,
                confidence=0.5,
                rationale="no registered tool; capability-only execution",
            )
            self._decisions.append(sel)
            return sel

        best_score, best = scored[0]
        alts = [
            {"tool": s.name, "confidence": sc, "capability": s.capability}
            for sc, s in scored[1:4]
        ]
        sel = ToolSelection(
            tool=best.name,
            capability=capability,
            confidence=min(0.99, best_score),
            alternatives=alts,
            rationale=f"selected {best.name} for {capability}",
        )
        self._decisions.append(sel)
        return sel

    @property
    def recent_decisions(self) -> list[dict[str, Any]]:
        return [d.to_dict() for d in self._decisions[-50:]]
