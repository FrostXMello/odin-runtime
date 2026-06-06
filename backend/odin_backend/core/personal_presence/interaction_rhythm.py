from __future__ import annotations


def rhythm(*, energy: float) -> str:
    return "steady" if energy < 0.7 else "animated"
