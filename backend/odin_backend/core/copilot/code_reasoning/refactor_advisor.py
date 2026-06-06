from __future__ import annotations

from typing import Any


def advise_refactor(*, file_path: str, smell: str) -> dict[str, Any]:
    actions = {
        "long_function": ["Extract helper functions", "Add unit tests for extracted parts"],
        "duplicate_code": ["Extract shared module", "Apply DRY at boundary"],
        "god_class": ["Split responsibilities", "Introduce service layer"],
    }
    return {"file": file_path, "smell": smell, "actions": actions.get(smell, ["Review structure manually"])}
