from __future__ import annotations


def deps_for(repo: str) -> list[str]:
    return [f"{repo}-core", f"{repo}-api"]
