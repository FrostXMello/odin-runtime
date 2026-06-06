from __future__ import annotations

from typing import Any


def editing_context(*, open_files: list[str]) -> dict[str, Any]:
    return {"open_files": len(open_files), "multi_file": len(open_files) > 1}
