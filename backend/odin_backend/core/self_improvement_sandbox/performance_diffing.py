from __future__ import annotations


def diff_perf(before: dict, after: dict) -> dict:
    return {"before": before, "after": after, "delta": after != before}
