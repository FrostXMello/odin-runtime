from __future__ import annotations


def reason(frames: list[str]) -> dict:
    return {"root_frame": frames[0] if frames else "", "depth": len(frames)}
