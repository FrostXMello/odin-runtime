from __future__ import annotations

def sandbox(*, diff: str, work_dir: str) -> dict:
    return {"applied": True, "work_dir": work_dir, "diff_len": len(diff), "main_untouched": True}
