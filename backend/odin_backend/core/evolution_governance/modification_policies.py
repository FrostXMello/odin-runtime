from __future__ import annotations

def policies() -> dict:
    return {
        "no_main_commit": True,
        "branch_isolation": True,
        "rollback_mandatory": True,
        "internet_patch_ingestion": False,
    }
