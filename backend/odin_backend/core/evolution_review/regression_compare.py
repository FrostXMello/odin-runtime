from __future__ import annotations


def compare(before: dict, after: dict) -> dict:
    return {"delta_keys": list(set(after.keys()) - set(before.keys())), "risk": "medium"}
