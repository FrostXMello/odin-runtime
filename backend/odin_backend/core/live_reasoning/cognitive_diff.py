from __future__ import annotations


def diff_branches(a: str, b: str) -> dict:
    return {"a": a[:120], "b": b[:120], "divergence": a != b}
