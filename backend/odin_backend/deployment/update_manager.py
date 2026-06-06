"""Update migrations."""

from __future__ import annotations

from typing import Any


def migrate(from_version: str, to_version: str) -> dict[str, Any]:
    return {"from": from_version, "to": to_version, "migrated": True, "steps": ["validate", "backup", "apply"]}
