"""Planner validation orchestration."""

from __future__ import annotations

from typing import Any

from odin_backend.core.planning.contracts import DynamicExecutionContract, ValidationRule
from odin_backend.core.planning.output_validation import validate_contract_output
from odin_backend.core.planning.consistency import check_plan_consistency
from odin_backend.core.planning.execution_verifier import verify_execution_result
from odin_backend.models.task_graph import TaskGraph


class PlanValidator:
    def validate_plan(self, graph: TaskGraph, contracts: dict[str, dict[str, Any]]) -> dict[str, Any]:
        consistency = check_plan_consistency(graph)
        missing_caps = []
        for nid, raw in contracts.items():
            c = DynamicExecutionContract.from_task_output(raw) if isinstance(raw, dict) else raw
            if c.type == "execution" and not c.capability:
                missing_caps.append(nid)
        return {
            "consistent": consistency["ok"],
            "issues": consistency.get("issues", []) + [f"missing capability: {x}" for x in missing_caps],
        }

    def validate_task_output(
        self,
        contract: DynamicExecutionContract,
        result: dict[str, Any],
    ) -> dict[str, Any]:
        ok, issues = validate_contract_output(contract, result)
        verified = verify_execution_result(contract, result)
        return {"valid": ok and verified["ok"], "issues": issues + verified.get("issues", [])}
