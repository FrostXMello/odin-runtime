from __future__ import annotations

from typing import Any


def generate_patch(*, file_path: str, goal: str, content: str) -> dict[str, Any]:
    preview = content[:120].replace("\n", "\\n")
    return {
        "file": file_path,
        "goal": goal,
        "patch_id": f"patch-{abs(hash(file_path + goal)) % 10_000_000}",
        "preview": preview,
        "incremental": True,
    }
