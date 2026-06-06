"""Environment validation."""

from __future__ import annotations

import sys
from typing import Any


def validate_environment() -> dict[str, Any]:
    issues: list[str] = []
    if sys.version_info < (3, 11):
        issues.append("python_version_below_3_11")
    return {"valid": len(issues) == 0, "issues": issues, "python": sys.version}
