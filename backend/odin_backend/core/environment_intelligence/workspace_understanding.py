from __future__ import annotations


def understand(*, repo: str, file: str = "") -> dict:
    return {"repo": repo, "file": file, "intent": "engineering" if file else "explore"}
