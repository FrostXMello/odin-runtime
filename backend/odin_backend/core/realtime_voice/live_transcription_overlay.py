from __future__ import annotations

def overlay(*, partial: str) -> dict:
    return {"partial": partial[-120:], "streaming": True}
