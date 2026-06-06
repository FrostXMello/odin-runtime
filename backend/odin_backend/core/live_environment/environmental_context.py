from __future__ import annotations

def context(*, on_battery: bool, heavy_load: bool) -> dict:
    return {"on_battery": on_battery, "heavy_load": heavy_load, "local_only": True}
