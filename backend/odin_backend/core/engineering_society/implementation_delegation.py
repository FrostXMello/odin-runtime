from __future__ import annotations


def delegate(*, role: str, task: str) -> dict:
    return {"role": role, "task": task[:80], "supervised": True}
