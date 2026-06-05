"""Output validation against dynamic contracts."""

from __future__ import annotations

from typing import Any

from odin_backend.core.planning.contracts import DynamicExecutionContract, ValidationRule


def validate_contract_output(
    contract: DynamicExecutionContract,
    result: dict[str, Any],
) -> tuple[bool, list[str]]:
    issues: list[str] = []
    for rule in contract.validation:
        ok, msg = _apply_rule(rule, result, contract.expected_output)
        if not ok:
            issues.append(msg)
    if contract.expected_output and not contract.validation:
        ok, msg = _apply_rule(ValidationRule(kind="exists", target=contract.expected_output), result, contract.expected_output)
        if not ok:
            issues.append(msg)
    return len(issues) == 0, issues


def _apply_rule(rule: ValidationRule, result: dict[str, Any], expected: str | None) -> tuple[bool, str]:
    target = rule.target or expected or ""
    if rule.kind == "exists":
        if target in result or result.get("path") == target:
            return True, ""
        if result.get("output") and target in str(result.get("output")):
            return True, ""
        return False, f"expected output missing: {target}"
    if rule.kind == "non_empty":
        if result:
            return True, ""
        return False, "empty result"
    if rule.kind == "schema":
        for key in rule.json_schema:
            if key not in result:
                return False, f"schema key missing: {key}"
        return True, ""
    return True, ""
