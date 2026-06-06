from __future__ import annotations

from typing import Any


def assess_risk(*, files: list[str], touches_main: bool) -> dict[str, Any]:
    risk = "critical" if touches_main else "high" if len(files) > 10 else "medium" if len(files) > 3 else "low"
    return {"risk": risk, "files": len(files), "requires_approval": risk != "low"}
