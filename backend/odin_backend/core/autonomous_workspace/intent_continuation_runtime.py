from __future__ import annotations


def continue_intent(*, intent: str) -> dict:
    return {"intent": intent[:120], "continued": True}
