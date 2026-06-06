from __future__ import annotations


def route(*, focus: str) -> dict:
    return {"primary": focus[:60], "secondary": "background"}
