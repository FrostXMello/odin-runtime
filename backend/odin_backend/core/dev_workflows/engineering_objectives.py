from __future__ import annotations

from typing import Any
from uuid import uuid4


def create_objective(*, title: str, repo: str) -> dict[str, Any]:
    return {"id": str(uuid4()), "title": title, "repo": repo, "status": "active"}
