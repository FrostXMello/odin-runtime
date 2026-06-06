from __future__ import annotations


def validate(*, branch: str) -> dict:
    return {"branch": branch, "validated": True, "production_deploy": False}
