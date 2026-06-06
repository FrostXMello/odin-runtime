from __future__ import annotations


def bridge(*, projects: list[str]) -> dict:
    return {"projects": projects[:8], "linked": len(projects) > 1}
