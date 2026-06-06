from __future__ import annotations


def recurrence(issues: list[str]) -> dict:
    seen: dict[str, int] = {}
    for i in issues:
        seen[i] = seen.get(i, 0) + 1
    return {"recurring": [k for k, v in seen.items() if v > 1]}
