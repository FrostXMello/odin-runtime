"""Post-execution verification."""

from __future__ import annotations

from typing import Any

from odin_backend.core.planning.contracts import DynamicExecutionContract


def verify_execution_result(contract: DynamicExecutionContract, result: dict[str, Any]) -> dict[str, Any]:
    issues: list[str] = []
    if contract.type == "validation" and not result:
        issues.append("validation produced no result")
    if result.get("success") is False:
        issues.append(result.get("error") or "execution reported failure")
    exit_code = result.get("exit_code")
    if exit_code is not None and int(exit_code) != 0 and contract.blocking:
        issues.append(f"non-zero exit code: {exit_code}")
    return {"ok": len(issues) == 0, "issues": issues}
