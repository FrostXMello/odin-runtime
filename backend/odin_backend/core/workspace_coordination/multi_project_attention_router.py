from __future__ import annotations


def route(*, projects: list[str]) -> dict:
    return {"primary": projects[0] if projects else "local", "secondary": projects[1:3]}
