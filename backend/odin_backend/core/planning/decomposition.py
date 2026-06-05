"""Semantic task decomposition."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from odin_backend.core.planning.contracts import DynamicExecutionContract, ValidationRule, contract_for_step
from odin_backend.core.planning.execution_strategy import ExecutionStrategy, StrategyKind
from odin_backend.core.planning.objectives import ParsedObjective


@dataclass
class DecomposedStep:
    goal: str
    capability: str
    tool: str | None
    params: dict[str, Any]
    confidence: float
    blocking: bool = True
    parallelizable: bool = False
    step_kind: str = "mission_step"
    expected_output: str | None = None
    validation_after: bool = False


@dataclass
class CapabilityRequirement:
    capability: str
    reason: str
    confidence: float = 0.8
    alternatives: list[str] = field(default_factory=list)


def infer_capability(parsed: ParsedObjective, goal: str) -> CapabilityRequirement:
    lower = goal.lower()
    if any(k in lower for k in ("search", "research", "web", "google")):
        return CapabilityRequirement("web.search", "research step", 0.82, ["api.http"])
    if any(k in lower for k in ("http", "api", "endpoint", "request")):
        return CapabilityRequirement("api.http", "api interaction", 0.8, ["web.search"])
    if any(k in lower for k in ("read file", "write file", "directory", "filesystem")):
        cap = "filesystem.write" if "write" in lower else "filesystem.read"
        return CapabilityRequirement(cap, "filesystem operation", 0.85)
    if any(k in lower for k in ("shell", "terminal", "command")):
        return CapabilityRequirement("shell.safe", "shell execution", 0.7, ["python.safe"])
    if any(k in lower for k in ("workflow", "pipeline", "orchestr")):
        return CapabilityRequirement("workflow.execute", "workflow step", 0.78)
    if parsed.domain == "execution" or "execute" in lower or "run" in lower:
        return CapabilityRequirement("python.safe", "code execution", 0.84, ["shell.safe"])
    if "verify" in lower or "validate" in lower:
        return CapabilityRequirement("python.safe", "validation script", 0.8)
    return CapabilityRequirement("python.safe", "default safe execution", 0.75, ["shell.safe"])


def infer_tool(capability: str) -> str | None:
    mapping = {
        "filesystem.read": "read_file",
        "filesystem.write": "write_file",
        "web.search": "search_web",
        "api.http": "search_web",
        "shell.safe": "execute_terminal",
        "python.safe": None,
        "workflow.execute": None,
    }
    return mapping.get(capability)


def decompose_objective(
    parsed: ParsedObjective,
    strategy: ExecutionStrategy,
    *,
    mission_id: str | None = None,
) -> list[DecomposedStep]:
    segments = _segment(parsed.raw)
    if len(segments) < 2:
        segments = [
            f"Analyze: {parsed.raw[:100]}",
            f"Execute: {parsed.raw[:100]}",
            f"Verify: {parsed.raw[:80]}",
        ]

    steps: list[DecomposedStep] = []
    for i, segment in enumerate(segments):
        req = infer_capability(parsed, segment)
        tool = infer_tool(req.capability)
        blocking = strategy.kind != StrategyKind.PARALLEL_WAVES or i == len(segments) - 1
        parallelizable = strategy.parallelizable and i > 0 and i < len(segments) - 1
        params: dict[str, Any] = {"mission_id": mission_id, "segment": segment[:200]}
        if req.capability == "python.safe":
            params["code"] = f"print({repr(segment[:120])})"
        elif tool:
            params["query"] = segment[:120]

        steps.append(
            DecomposedStep(
                goal=segment,
                capability=req.capability,
                tool=tool,
                params=params,
                confidence=req.confidence,
                blocking=blocking,
                parallelizable=parallelizable,
                validation_after="verify" in segment.lower() or i == len(segments) - 1,
            )
        )

    if strategy.validation_first and steps:
        steps.insert(
            0,
            DecomposedStep(
                goal=f"Preflight validation: {parsed.raw[:60]}",
                capability="python.safe",
                tool=None,
                params={"code": "print('preflight_ok')"},
                confidence=0.9,
                blocking=True,
                step_kind="validation",
                validation_after=False,
            ),
        )

    return steps


def steps_to_contracts(steps: list[DecomposedStep]) -> dict[int, DynamicExecutionContract]:
    contracts: dict[int, DynamicExecutionContract] = {}
    for i, step in enumerate(steps):
        validation: list[ValidationRule] = []
        if step.validation_after and step.expected_output:
            validation.append(ValidationRule(kind="exists", target=step.expected_output))
        elif step.validation_after:
            validation.append(ValidationRule(kind="non_empty", target="result"))
        contracts[i] = contract_for_step(
            goal=step.goal,
            capability=step.capability,
            tool=step.tool,
            params=step.params,
            confidence=step.confidence,
            expected_output=step.expected_output,
            blocking=step.blocking,
            parallelizable=step.parallelizable,
            validation=validation,
        )
        contracts[i].type = step.step_kind if step.step_kind != "mission_step" else "execution"
    return contracts


def _segment(objective: str) -> list[str]:
    text = objective.strip()
    for sep in (" then ", ";", "\n", " and then "):
        if sep in text.lower():
            parts = [p.strip() for p in text.replace(sep, "|").split("|") if p.strip()]
            if len(parts) >= 2:
                return parts
    if "." in text:
        parts = [p.strip() for p in text.split(".") if p.strip()]
        if len(parts) >= 2:
            return parts
    return [text] if text else []
