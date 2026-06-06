def cinematic(enabled: bool) -> dict:
    return {"enabled": enabled, "fps_cap": 60 if enabled else 30, "progressive_render": enabled}
