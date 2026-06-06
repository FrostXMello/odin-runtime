from __future__ import annotations

def memory_map(*, threads: int) -> dict:
    return {"threads": threads, "active_cells": min(threads, 8)}
