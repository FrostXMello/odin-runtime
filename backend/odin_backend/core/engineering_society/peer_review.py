from __future__ import annotations


def review(*, patch: str) -> dict:
    return {"approved": False, "notes": "supervised review required", "patch_len": len(patch)}
