from __future__ import annotations


def hint(*, workflow: str) -> dict:
    return {"hint": f"Consider reviewing {workflow[:40]}", "non_invasive": True}
