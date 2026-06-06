from __future__ import annotations


def route(*, profile: str) -> list[str]:
    if profile in ("survival", "lightweight"):
        return ["kernel:runtime"]
    return ["kernel:runtime", "cognitive-streams:runtime", "memory-fabric:runtime"]
