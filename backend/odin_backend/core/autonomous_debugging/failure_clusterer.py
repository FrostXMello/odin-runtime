from __future__ import annotations


def cluster(failures: list[str]) -> dict:
    groups: dict[str, int] = {}
    for f in failures:
        key = f.split(":")[0][:40]
        groups[key] = groups.get(key, 0) + 1
    return {"clusters": groups, "repeated": [k for k, v in groups.items() if v > 1]}
