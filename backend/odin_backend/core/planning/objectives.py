"""Objective interpretation and intent inference."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ParsedObjective:
    raw: str
    intent: str
    verbs: list[str] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    domain: str = "general"

    def to_dict(self) -> dict[str, Any]:
        return {
            "raw": self.raw,
            "intent": self.intent,
            "verbs": self.verbs,
            "artifacts": self.artifacts,
            "constraints": self.constraints,
            "domain": self.domain,
        }


_VERBS = frozenset(
    {
        "analyze",
        "build",
        "create",
        "deploy",
        "execute",
        "fetch",
        "generate",
        "monitor",
        "read",
        "research",
        "run",
        "search",
        "summarize",
        "validate",
        "verify",
        "write",
    }
)

_DOMAIN_HINTS: dict[str, tuple[str, ...]] = {
    "filesystem": ("file", "directory", "folder", "read", "write"),
    "api": ("api", "http", "endpoint", "request", "webhook"),
    "research": ("search", "research", "investigate", "find"),
    "execution": ("run", "execute", "script", "shell", "python"),
    "workflow": ("workflow", "pipeline", "orchestrate", "mission"),
}


def parse_objective(objective: str) -> ParsedObjective:
    text = objective.strip()
    lower = text.lower()
    words = re.findall(r"[a-zA-Z_]+", lower)
    verbs = [w for w in words if w in _VERBS]
    artifacts: list[str] = []
    for pat in (r"[\w./-]+\.(json|csv|md|txt|py|yaml|yml)", r"report\b", r"summary\b"):
        artifacts.extend(re.findall(pat, lower) if pat.endswith("\\b") else re.findall(pat, text, re.I))

    constraints: list[str] = []
    if "safely" in lower or "safe" in lower:
        constraints.append("safe_execution")
    if "parallel" in lower:
        constraints.append("parallelizable")
    if "validate" in lower or "verify" in lower:
        constraints.append("requires_validation")

    domain = "general"
    best = 0
    for dom, hints in _DOMAIN_HINTS.items():
        score = sum(1 for h in hints if h in lower)
        if score > best:
            best = score
            domain = dom

    intent = verbs[0] if verbs else "execute"
    if " then " in lower or " and then " in lower:
        intent = "multi_step"
    elif domain == "research":
        intent = "research"
    elif domain == "filesystem":
        intent = "filesystem_ops"

    return ParsedObjective(
        raw=text,
        intent=intent,
        verbs=verbs or ["execute"],
        artifacts=list(dict.fromkeys(artifacts)),
        constraints=constraints,
        domain=domain,
    )
