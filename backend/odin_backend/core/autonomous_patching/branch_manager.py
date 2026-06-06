from __future__ import annotations
from uuid import uuid4

def create_branch(*, prefix: str = "odin-evolve") -> dict:
    return {"branch": f"{prefix}-{uuid4().hex[:8]}", "main_protected": True}
