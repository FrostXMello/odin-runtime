from __future__ import annotations

from typing import Any


def reason_about_repo(*, path: str, files: list[str]) -> dict[str, Any]:
    py = sum(1 for f in files if f.endswith(".py"))
    ts = sum(1 for f in files if f.endswith((".ts", ".tsx")))
    return {"path": path, "file_count": len(files), "python_files": py, "typescript_files": ts, "primary": "python" if py >= ts else "typescript"}
