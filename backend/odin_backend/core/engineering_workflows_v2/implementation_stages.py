from __future__ import annotations


STAGES = ("plan", "implement", "test", "review", "merge_proposal")


def advance(current: str) -> str:
    order = list(STAGES)
    try:
        idx = order.index(current)
        return order[min(idx + 1, len(order) - 1)]
    except ValueError:
        return "plan"
