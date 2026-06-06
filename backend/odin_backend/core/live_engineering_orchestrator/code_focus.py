from __future__ import annotations


def infer_goal(*, file: str, error: str = "") -> str:
    if error:
        return f"debug {file}"
    if file.endswith(".py"):
        return f"implement {file}"
    return f"review {file}"
