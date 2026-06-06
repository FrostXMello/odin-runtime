from __future__ import annotations


def checkpoint(stage: str, payload: dict) -> dict:
    return {"stage": stage, "payload": payload, "approval_gate": stage == "merge_proposal"}
