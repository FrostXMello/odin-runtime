from __future__ import annotations


def simulate(*, patch: str) -> dict:
    return {"simulated": True, "patch_len": len(patch), "auto_merge": False}
