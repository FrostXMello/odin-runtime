from __future__ import annotations

from typing import Any


def build_workflow(*, strategy: str) -> dict[str, Any]:
    steps = {
        "fix_imports": ["inspect sys.path", "verify package", "apply patch", "run tests"],
        "isolate_and_patch": ["reproduce", "localize", "patch in branch", "validate"],
        "escalate_operator": ["summarize findings", "request approval"],
    }
    return {"strategy": strategy, "steps": steps.get(strategy, ["analyze"]), "approval_required": True}
