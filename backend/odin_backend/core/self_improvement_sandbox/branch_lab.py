from __future__ import annotations


def create_branch(name: str) -> dict:
    return {"branch": f"sandbox/{name}", "isolated": True, "main_safe": True}
