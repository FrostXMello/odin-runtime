from __future__ import annotations


def prioritize(*, load: float) -> str:
    if load > 0.8:
        return "reasoning"
    if load > 0.5:
        return "engineering"
    return "workspace"
