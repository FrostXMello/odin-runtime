from __future__ import annotations


def score(*, repos: int, failures: int, pending: int) -> float:
    return min(1.0, (repos * 0.1 + failures * 0.2 + pending * 0.15))
